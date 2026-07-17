"""4 tool gia sư thích ứng — dùng bởi Planner Agent (bot hỏi-đáp). Mỗi tool tự mở
AsyncSession riêng vì Tool Registry chỉ truyền JSON args từ LLM, không inject session."""
from sqlalchemy import select

from db.connector import SessionLocal
from db.models import Question, Skill, Student
from domain.dashboard_queries import parent_dashboard_query, teacher_dashboard_query
from domain.knowledge_graph import load_knowledge_graph
from domain.mastery_store import record_response
from domain.practice_selector import generate_practice_path as _generate_practice_path
from tools.base import Tool

_graph = load_knowledge_graph()


async def diagnose_gap(student_id: int, answers: list[dict]) -> dict:
    async with SessionLocal() as session:
        results = []
        for answer in answers:
            result = await record_response(
                session=session,
                student_id=student_id,
                question_id=answer["question_id"],
                student_answer=answer["student_answer"],
                session_type="diagnostic",
                graph=_graph,
            )
            results.append(result)

        from domain.bkt import find_root_gaps
        from domain.mastery_store import get_mastery_snapshot

        mastery = await get_mastery_snapshot(session, student_id, _graph)
        root_gaps = find_root_gaps(_graph, mastery)

        return {
            "gaps": [
                {
                    "skill_code": code,
                    "skill_name": _graph.skill_name(code),
                    "confidence": round(1 - mastery[code].p_mastery, 2),
                    "grade": _graph.skill(code)["grade"],
                }
                for code in root_gaps
            ],
            "per_answer_results": results,
        }


async def generate_practice_path(student_id: int, max_items: int = 10) -> dict:
    async with SessionLocal() as session:
        path = await _generate_practice_path(session, student_id, _graph, max_items)
        return {"practice_path": path}


async def teacher_dashboard(class_id: int) -> dict:
    async with SessionLocal() as session:
        return await teacher_dashboard_query(session, class_id, _graph)


async def parent_dashboard(student_id: int, parent_id: int) -> dict:
    async with SessionLocal() as session:
        return await parent_dashboard_query(session, student_id, parent_id, _graph)


diagnose_gap_tool = Tool(
    name="diagnose_gap",
    description=(
        "Chấm bài kiểm tra chẩn đoán của học sinh (server tự chấm theo đáp án đúng, "
        "không tin is_correct từ bên ngoài), cập nhật mastery bằng Bayesian Knowledge "
        "Tracing, trả về gap đã xếp hạng theo nguyên nhân gốc."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "student_id": {"type": "integer"},
            "answers": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "question_id": {"type": "integer"},
                        "student_answer": {"type": "string"},
                    },
                    "required": ["question_id", "student_answer"],
                },
            },
        },
        "required": ["student_id", "answers"],
    },
    func=diagnose_gap,
)

generate_practice_path_tool = Tool(
    name="generate_practice_path",
    description="Sinh lộ trình luyện tập cá nhân hóa, lấp từ gap gốc sâu nhất đi lên.",
    input_schema={
        "type": "object",
        "properties": {
            "student_id": {"type": "integer"},
            "max_items": {"type": "integer", "default": 10},
        },
        "required": ["student_id"],
    },
    func=generate_practice_path,
)

teacher_dashboard_tool = Tool(
    name="teacher_dashboard_query",
    description=(
        "Tổng hợp dashboard giáo viên: heatmap kỹ năng theo lớp, xếp hạng ưu tiên học "
        "sinh, nhóm theo gap chung, cảnh báo lỗ hổng diện rộng."
    ),
    input_schema={
        "type": "object",
        "properties": {"class_id": {"type": "integer"}},
        "required": ["class_id"],
    },
    func=teacher_dashboard,
)

parent_dashboard_tool = Tool(
    name="parent_dashboard_query",
    description=(
        "Dashboard phụ huynh cho 1 con — tiến độ theo thời gian, gợi ý hoạt động tại "
        "nhà. Chỉ trả dữ liệu nếu parent_id khớp đúng phụ huynh của học sinh đó."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "student_id": {"type": "integer"},
            "parent_id": {"type": "integer"},
        },
        "required": ["student_id", "parent_id"],
    },
    func=parent_dashboard,
)
