"""Loader idempotent: domain/data/*.json → DB + 1 lớp/giáo viên/học sinh mẫu.

Chạy: python -m db.seed
"""
import asyncio
import json
from pathlib import Path

from sqlalchemy import select

from db.connector import SessionLocal, engine
from db.models import Base, ClassRoom, Parent, Question, Skill, SkillPrerequisite, Student, Teacher

DATA_DIR = Path(__file__).parent.parent / "domain" / "data"


async def seed_skills_and_questions(session) -> dict[str, int]:
    with open(DATA_DIR / "knowledge_graph.json", encoding="utf-8") as f:
        graph_data = json.load(f)

    skill_id_by_code: dict[str, int] = {}
    for s in graph_data["skills"]:
        existing = (
            await session.execute(select(Skill).where(Skill.code == s["code"]))
        ).scalar_one_or_none()
        if existing is None:
            existing = Skill(
                code=s["code"],
                name_vi=s["name_vi"],
                name_en=s["name_en"],
                grade=s["grade"],
                unit=s["unit"],
                skill_type=s["skill_type"],
                p_init=s["p_init"],
                p_transit=s["p_transit"],
                p_slip=s["p_slip"],
                p_guess=s["p_guess"],
            )
            session.add(existing)
            await session.flush()
        skill_id_by_code[s["code"]] = existing.id

    for edge in graph_data["edges"]:
        prereq_id = skill_id_by_code[edge["prerequisite"]]
        dep_id = skill_id_by_code[edge["dependent"]]
        existing = (
            await session.execute(
                select(SkillPrerequisite).where(
                    SkillPrerequisite.prerequisite_skill_id == prereq_id,
                    SkillPrerequisite.dependent_skill_id == dep_id,
                )
            )
        ).scalar_one_or_none()
        if existing is None:
            session.add(
                SkillPrerequisite(
                    prerequisite_skill_id=prereq_id,
                    dependent_skill_id=dep_id,
                    weight=edge.get("weight", 1.0),
                )
            )

    with open(DATA_DIR / "question_bank.json", encoding="utf-8") as f:
        questions_data = json.load(f)

    for q in questions_data:
        skill_id = skill_id_by_code[q["skill_code"]]
        existing = (
            await session.execute(
                select(Question).where(
                    Question.skill_id == skill_id, Question.content == q["content"]
                )
            )
        ).scalar_one_or_none()
        if existing is None:
            session.add(
                Question(
                    skill_id=skill_id,
                    content=q["content"],
                    question_type=q["question_type"],
                    options=q["options"],
                    correct_answer=q["correct_answer"],
                    difficulty=q["difficulty"],
                    source="teacher_digitized",
                )
            )

    await session.commit()
    return skill_id_by_code


async def seed_demo_class(session) -> None:
    teacher = (
        await session.execute(select(Teacher).where(Teacher.full_name == "Cô Ngọc"))
    ).scalar_one_or_none()
    if teacher is None:
        teacher = Teacher(full_name="Cô Ngọc")
        session.add(teacher)
        await session.flush()

    classroom = (
        await session.execute(select(ClassRoom).where(ClassRoom.name == "Lớp 3A"))
    ).scalar_one_or_none()
    if classroom is None:
        classroom = ClassRoom(name="Lớp 3A", teacher_id=teacher.id, grade=3)
        session.add(classroom)
        await session.flush()

    demo_students = ["Jordan Nico", "Karen Hope", "Nadila Adja", "Samantha William", "Tony Soap"]
    for name in demo_students:
        existing = (
            await session.execute(
                select(Student).where(
                    Student.full_name == name, Student.class_id == classroom.id
                )
            )
        ).scalar_one_or_none()
        if existing is None:
            parent = Parent(full_name=f"Phụ huynh {name}")
            session.add(parent)
            await session.flush()
            session.add(
                Student(full_name=name, class_id=classroom.id, parent_id=parent.id)
            )

    await session.commit()


async def main() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with SessionLocal() as session:
        await seed_skills_and_questions(session)
        await seed_demo_class(session)

    print("Seed hoàn tất.")


if __name__ == "__main__":
    asyncio.run(main())
