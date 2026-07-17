"""Seed data — import knowledge_graph.json + questions.json vào DB.

Chạy: python -m db.seed_data
"""
import asyncio
import json
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Skill, Question, Class, Student, Parent, ParentStudent

_DATA_DIR = Path(__file__).parent.parent / "ai"
_QUESTIONS_PATH = _DATA_DIR.parent / "tools" / "questions.json"


async def seed_skills(session: AsyncSession) -> int:
    """Import skills từ knowledge_graph.json."""
    path = _DATA_DIR / "knowledge_graph.json"
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    prereqs_map: dict[str, list[str]] = {}
    for edge in data.get("edges", []):
        to_node = edge["to"]
        from_node = edge["from"]
        if to_node not in prereqs_map:
            prereqs_map[to_node] = []
        prereqs_map[to_node].append(from_node)

    count = 0
    for s in data.get("nodes", data.get("skills", [])):
        sid = s.get("skill_id", s.get("id"))
        exists = await session.execute(
            select(Skill).where(Skill.id == sid)
        )
        if exists.scalars().first():
            continue

        grade = s.get("grade", 3)
        unit = s.get("unit_name", s.get("unit", ""))
        name = s.get("lesson_title", s.get("name_vi", s.get("name_en", "")))
        skill_type = s.get("skill_type", "vocabulary" if "vocabulary" in name.lower() else "grammar" if "grammar" in name.lower() else "other")

        skill = Skill(
            id=sid,
            code_gdpt=s.get("code_gdpt", sid),
            name_vi=name,
            name_en=s.get("name_en", name),
            grade=grade,
            unit=unit,
            skill_type=skill_type,
            p_init=s.get("p_init", 0.3),
            p_transit=s.get("p_transit", 0.3),
            p_slip=s.get("p_slip", 0.1),
            p_guess=s.get("p_guess", 0.2),
            prerequisites=",".join(prereqs_map.get(sid, s.get("prerequisites", []))),
        )
        session.add(skill)
        count += 1

    await session.flush()
    return count


async def seed_questions_from_json(session: AsyncSession) -> int:
    """Import questions từ questions.json."""
    if not _QUESTIONS_PATH.exists():
        return 0

    with open(_QUESTIONS_PATH, encoding="utf-8") as f:
        data = json.load(f)

    count = 0
    for q in data.get("questions", []):
        qid = q.get("question_id", q.get("id"))
        exists = await session.execute(
            select(Question).where(Question.question_id == qid)
        )
        if exists.scalars().first():
            continue

        question = Question(
            question_id=qid,
            type=q.get("type", "read_choice"),
            instruction_label=q.get("instruction_label", "DOC & CHON"),
            skill_id=q["skill_id"],
            skill_name=q.get("skill_name", q["skill_id"]),
            difficulty=str(q.get("difficulty", "easy")),
            purpose=q.get("purpose", "diagnostic"),
            prompt=q.get("prompt"),
            options=q.get("options"),
            correct_option_id=q.get("correct_option_id", "a"),
            explanation=q.get("explanation"),
        )
        session.add(question)
        count += 1

    await session.flush()
    return count


async def seed_sample_data(session: AsyncSession) -> dict:
    """Tạo data mẫu: 1 lớp, 5 học sinh, 2 phụ huynh."""
    result = {"classes": 0, "students": 0, "parents": 0}

    cls = Class(id="CLASS01", name="Lop 3A1", grade=3)
    exists = await session.execute(select(Class).where(Class.id == "CLASS01"))
    if not exists.scalars().first():
        session.add(cls)
        result["classes"] = 1

    students_data = [
        ("STU01", "Le Van An", "CLASS01"),
        ("STU02", "Pham Thi Bich", "CLASS01"),
        ("STU03", "Hoang Van Cuong", "CLASS01"),
        ("STU04", "Nguyen Thi Dao", "CLASS01"),
        ("STU05", "Vo Van Em", "CLASS01"),
    ]
    for sid, name, cid in students_data:
        exists = await session.execute(select(Student).where(Student.id == sid))
        if not exists.scalars().first():
            session.add(Student(id=sid, name=name, class_id=cid))
            result["students"] += 1

    parents_data = [
        ("PAR01", "Le Van F", "0901234567"),
        ("PAR02", "Pham Thi G", "0912345678"),
    ]
    for pid, name, phone in parents_data:
        exists = await session.execute(select(Parent).where(Parent.id == pid))
        if not exists.scalars().first():
            session.add(Parent(id=pid, name=name, phone=phone))
            result["parents"] += 1

    parent_student_links = [
        ("PAR01", "STU01"),
        ("PAR02", "STU02"),
        ("PAR02", "STU03"),
    ]
    for pid, sid in parent_student_links:
        exists = await session.execute(
            select(ParentStudent).where(
                ParentStudent.parent_id == pid,
                ParentStudent.student_id == sid,
            )
        )
        if not exists.scalars().first():
            session.add(ParentStudent(parent_id=pid, student_id=sid))

    await session.flush()
    return result


async def run_seed() -> None:
    """Chạy seed standalone."""
    from db.connector import SessionLocal, engine
    from db.models import Base

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with SessionLocal() as session:
        async with session.begin():
            skills = await seed_skills(session)
            questions = await seed_questions_from_json(session)
            sample = await seed_sample_data(session)

    print(f"Seed complete:")
    print(f"  Skills: {skills} new")
    print(f"  Questions: {questions} new")
    print(f"  Classes: {sample['classes']}")
    print(f"  Students: {sample['students']}")
    print(f"  Parents: {sample['parents']}")


if __name__ == "__main__":
    asyncio.run(run_seed())
