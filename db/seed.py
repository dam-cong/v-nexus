"""Seed demo data for V-Nexus Tutor."""
import json
import os
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import (
    Student, Teacher, Ranking,
    Question, PlacementTest, PlacementTestQuestion, StudentTestResult,
)
from db.password import hash_password

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "docs", "data")


DEMO_TEACHERS = [
    {"name": "Nguyen Thi Lan", "email": "teacher1@vnexus.vn", "subject": "Tieng Anh", "role_id": 2},
    {"name": "Tran Minh Hung", "email": "teacher2@vnexus.vn", "subject": "Tieng Anh", "role_id": 2},
]

DEMO_ADMINS = [
    {"name": "Admin VNexus", "email": "admin@vnexus.vn", "subject": None, "role_id": 3},
]

DEMO_STUDENTS = [
    {"name": "Le Van An", "email": "hs01@vnexus.vn", "grade": "Lop 3"},
    {"name": "Pham Thi Bich", "email": "hs02@vnexus.vn", "grade": "Lop 3"},
    {"name": "Hoang Van Cuong", "email": "hs03@vnexus.vn", "grade": "Lop 4"},
    {"name": "Nguyen Thi Dao", "email": "hs04@vnexus.vn", "grade": "Lop 4"},
    {"name": "Vo Van Em", "email": "hs05@vnexus.vn", "grade": "Lop 3"},
]


def _load_json(filename: str) -> dict:
    path = os.path.join(DATA_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


async def seed_data(session: AsyncSession) -> None:
    """Seed demo users if tables are empty."""
    result = await session.execute(select(Teacher).limit(1))
    if result.scalars().first():
        return  # Already seeded

    default_password = hash_password("123456")

    # Seed teachers + admins
    for t in DEMO_TEACHERS + DEMO_ADMINS:
        teacher = Teacher(
            name=t["name"],
            email=t["email"],
            hashed_password=default_password,
            role_id=t["role_id"],
            subject=t.get("subject"),
        )
        session.add(teacher)

    await session.flush()

    # Seed students
    for s in DEMO_STUDENTS:
        student = Student(
            name=s["name"],
            email=s["email"],
            hashed_password=default_password,
            grade=s["grade"],
            role_id=1,
        )
        session.add(student)

    await session.flush()

    # Create rankings for students
    result = await session.execute(select(Student))
    students = result.scalars().all()
    for i, student in enumerate(students):
        ranking = Ranking(
            student_id=student.id,
            score=(len(students) - i) * 15,
            level="Beginner" if i > 2 else "Elementary",
        )
        session.add(ranking)

    await session.commit()


async def seed_questions(session: AsyncSession) -> None:
    """Seed question bank from question-bank.json."""
    result = await session.execute(select(Question).limit(1))
    if result.scalars().first():
        return

    data = _load_json("question-bank.json")
    for q in data["questions"]:
        question = Question(
            question_id=q["question_id"],
            type=q["type"],
            instruction_label=q["instruction_label"],
            skill_id=q["skill_id"],
            skill_name=q["skill_name"],
            difficulty=q["difficulty"],
            purpose=q["purpose"],
            prompt=q["prompt"],
            options=q["options"],
            correct_option_id=q["correct_option_id"],
            explanation=q.get("explanation"),
        )
        session.add(question)

    await session.commit()


async def seed_placement_tests(session: AsyncSession) -> None:
    """Seed placement test from placement-test.json."""
    result = await session.execute(select(PlacementTest).limit(1))
    if result.scalars().first():
        return

    data = _load_json("placement-test.json")

    test = PlacementTest(
        test_id=data["test_id"],
        title=data["title"],
        mascot=data.get("mascot"),
        steps=data.get("steps"),
        levels=data.get("levels"),
        adaptive_config=data.get("adaptive_config"),
    )
    session.add(test)
    await session.flush()

    # Map question_id -> Question.id
    q_map: dict[str, int] = {}
    q_result = await session.execute(select(Question))
    for q in q_result.scalars().all():
        q_map[q.question_id] = q.id

    # Map placement question_id (q_001..q_014) -> question bank id
    # The placement test questions share the same content but have different IDs
    # We need to find matching questions by skill_id + correct_option
    pt_result = await session.execute(select(Question))
    all_questions = {q.question_id: q for q in pt_result.scalars().all()}

    # Build a lookup by (skill_id, correct_option_id) for matching
    skill_correct_map: dict[tuple, int] = {}
    for q in all_questions.values():
        key = (q.skill_id, q.correct_option_id)
        if key not in skill_correct_map:
            skill_correct_map[key] = q.id

    for pt_q in data["questions"]:
        key = (pt_q["skill_id"], pt_q["correct_option_id"])
        q_db_id = skill_correct_map.get(key)
        if not q_db_id:
            continue

        link = PlacementTestQuestion(
            test_id=test.id,
            question_id=q_db_id,
            order_num=pt_q["order"],
        )
        session.add(link)

    await session.commit()


async def seed_test_results(session: AsyncSession) -> None:
    """Seed student test results from survey-results.json."""
    result = await session.execute(select(StudentTestResult).limit(1))
    if result.scalars().first():
        return

    data = _load_json("survey-results.json")

    # Map email -> Student.id
    student_map: dict[str, int] = {}
    s_result = await session.execute(select(Student))
    for s in s_result.scalars().all():
        student_map[s.email] = s.id

    # Get placement test id
    pt_result = await session.execute(select(PlacementTest))
    pt = pt_result.scalars().first()
    if not pt:
        return

    for r in data["results"]:
        student_id = student_map.get(r["email"])
        if not student_id:
            continue

        test_result = StudentTestResult(
            student_id=student_id,
            test_id=pt.id,
            answers=r.get("answers"),
            score=r["score"],
            max_score=r["max_score"],
            percentage=r["percentage"],
            result_level=r["result_level"],
            cefr=r["cefr"],
            time_total_sec=r.get("time_total_sec", 0),
            mastery=r.get("mastery"),
            gaps=r.get("gaps"),
            recommendations=r.get("recommendations"),
            test_date=datetime.fromisoformat(r["test_date"].replace("Z", "")).replace(tzinfo=None),
        )
        session.add(test_result)

    await session.commit()
