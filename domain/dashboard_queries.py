"""Truy vấn tổng hợp cho dashboard giáo viên & phụ huynh — trên StudentSkillMastery/StudentResponse."""
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Skill, Student, StudentResponse, StudentSkillMastery
from domain.bkt import FAIL_THRESHOLD, MASTERED_THRESHOLD, find_root_gaps
from domain.knowledge_graph import KnowledgeGraph
from domain.mastery_store import get_mastery_snapshot

CLASS_WIDE_ALERT_RATIO = 0.4

# Gợi ý hoạt động tại nhà theo skill_type — template cố định, KHÔNG gọi LLM (giữ dashboard
# phụ huynh rẻ, đúng tinh thần "LLM narration là lớp online cộng thêm").
HOME_ACTIVITY_BY_SKILL_TYPE = {
    "phonics": "Cùng con đọc to bảng chữ cái 10 phút/ngày.",
    "vocab": "Chơi flashcard từ vựng với con 15 phút/ngày.",
    "grammar": "Cùng con đặt 3 câu mẫu với cấu trúc đang học mỗi tối.",
    "listening": "Cho con nghe lại đoạn hội thoại mẫu và nhắc lại theo.",
    "speaking": "Luyện hỏi-đáp ngắn bằng tiếng Anh với con trước khi đi ngủ.",
}


async def teacher_dashboard_query(session: AsyncSession, class_id: int, graph: KnowledgeGraph) -> dict:
    students = (
        await session.execute(select(Student).where(Student.class_id == class_id))
    ).scalars().all()

    heatmap: dict[str, dict] = {code: {"weak_count": 0} for code in graph.skill_codes()}
    priority_rows = []
    student_root_gaps: dict[int, list[str]] = {}

    for student in students:
        mastery = await get_mastery_snapshot(session, student.id, graph)
        for code, state in mastery.items():
            if state.p_mastery < FAIL_THRESHOLD:
                heatmap[code]["weak_count"] += 1

        root_gaps = find_root_gaps(graph, mastery)
        student_root_gaps[student.id] = root_gaps

        stuck_row = (
            await session.execute(
                select(StudentSkillMastery).where(
                    StudentSkillMastery.student_id == student.id,
                    StudentSkillMastery.stuck_since.is_not(None),
                )
            )
        ).scalars().first()
        days_stuck = (datetime.utcnow() - stuck_row.stuck_since).days if stuck_row else 0

        if root_gaps:
            worst_code = root_gaps[0]
            priority_rows.append(
                {
                    "student_id": student.id,
                    "student_name": student.full_name,
                    "root_gap_skill_code": worst_code,
                    "root_gap_skill_name": graph.skill_name(worst_code),
                    "p_mastery": mastery[worst_code].p_mastery,
                    "days_stuck": days_stuck,
                    "num_gaps": len(root_gaps),
                }
            )

    total_students = len(students) or 1
    heatmap_pct = {
        code: round(info["weak_count"] / total_students * 100, 1)
        for code, info in heatmap.items()
    }

    class_alerts = [
        {
            "skill_code": code,
            "skill_name": graph.skill_name(code),
            "pct_weak": pct,
        }
        for code, pct in heatmap_pct.items()
        if pct / 100 >= CLASS_WIDE_ALERT_RATIO
    ]

    priority_rows.sort(key=lambda r: (-r["num_gaps"], r["p_mastery"]))

    groups: dict[str, list[str]] = {}
    for student_id, gaps in student_root_gaps.items():
        if not gaps:
            continue
        key = gaps[0]
        groups.setdefault(key, []).append(
            next(s.full_name for s in students if s.id == student_id)
        )

    return {
        "class_id": class_id,
        "total_students": len(students),
        "heatmap": heatmap_pct,
        "priority_ranking": priority_rows,
        "class_alerts": class_alerts,
        "groups_by_shared_gap": [
            {"skill_code": code, "skill_name": graph.skill_name(code), "students": names}
            for code, names in groups.items()
        ],
    }


async def parent_dashboard_query(
    session: AsyncSession, student_id: int, parent_id: int, graph: KnowledgeGraph
) -> dict:
    student = (
        await session.execute(select(Student).where(Student.id == student_id))
    ).scalar_one_or_none()

    if student is None or student.parent_id != parent_id:
        return {"error": "access_denied"}

    mastery = await get_mastery_snapshot(session, student_id, graph)

    responses = (
        await session.execute(
            select(StudentResponse, Skill.code, Skill.skill_type)
            .join(Skill, Skill.id == StudentResponse.skill_id)
            .where(StudentResponse.student_id == student_id)
            .order_by(StudentResponse.answered_at.asc())
        )
    ).all()
    timeline = [
        {
            "skill_code": code,
            "answered_at": r.answered_at.isoformat(),
            "p_mastery_after": r.p_mastery_after,
        }
        for r, code, _skill_type in responses
    ]

    stuck_row = (
        await session.execute(
            select(StudentSkillMastery, Skill.code, Skill.skill_type)
            .join(Skill, Skill.id == StudentSkillMastery.skill_id)
            .where(
                StudentSkillMastery.student_id == student_id,
                StudentSkillMastery.stuck_since.is_not(None),
            )
        )
    ).first()

    stuck_flag = None
    suggestion = None
    if stuck_row:
        row, code, skill_type = stuck_row
        days_stuck = (datetime.utcnow() - row.stuck_since).days
        stuck_flag = {
            "skill_code": code,
            "skill_name": graph.skill_name(code),
            "days_stuck": days_stuck,
        }
        suggestion = HOME_ACTIVITY_BY_SKILL_TYPE.get(
            skill_type, "Cùng con ôn lại bài gần nhất 15 phút/ngày."
        )

    return {
        "student_id": student_id,
        "student_name": student.full_name,
        "progress_timeline": timeline,
        "stuck_flag": stuck_flag,
        "suggested_home_activity": suggestion,
        "mastery_snapshot": {code: state.p_mastery for code, state in mastery.items()},
    }
