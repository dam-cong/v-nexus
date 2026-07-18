"""Seed demo data for V-Nexus Tutor."""
import json
import os
from datetime import datetime
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import (
    User, Student, Teacher, Ranking,
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
    {"name": "Đàm Công Hiến", "email": "hiendc@gmail.com", "grade": "Lớp 6", "password": "88888888"},
]


def _load_json(filename: str) -> dict:
    path = os.path.join(DATA_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


async def seed_data(session: AsyncSession) -> None:
    """Seed demo users if tables are empty."""
    result = await session.execute(select(User).limit(1))
    if result.scalars().first():
        return  # Already seeded

    default_password = hash_password("123456")

    # Seed teachers + admins (role 2/3)
    for t in DEMO_TEACHERS + DEMO_ADMINS:
        user = User(
            name=t["name"],
            email=t["email"],
            hashed_password=default_password,
            role_id=t["role_id"],
        )
        session.add(user)
        await session.flush()
        session.add(Teacher(user_id=user.id, subject=t.get("subject")))

    await session.flush()

    # Seed students (role 1)
    for s in DEMO_STUDENTS:
        pw = hash_password(s["password"]) if s.get("password") else default_password
        user = User(
            name=s["name"],
            email=s["email"],
            hashed_password=pw,
            role_id=1,
        )
        session.add(user)
        await session.flush()
        session.add(Student(user_id=user.id, grade=s["grade"]))

    await session.flush()

    # Create rankings for students
    result = await session.execute(select(User).where(User.role_id == 1))
    students = result.scalars().all()
    for i, user in enumerate(students):
        ranking = Ranking(
            user_id=user.id,
            score=(len(students) - i) * 15,
            level="Beginner" if i > 2 else "Elementary",
        )
        session.add(ranking)

    await session.commit()


async def seed_questions(session: AsyncSession) -> None:
    """Seed question bank from question-bank.json."""
    data = _load_json("question-bank.json")
    existing_result = await session.execute(select(Question))
    existing = {q.question_id: q for q in existing_result.scalars().all()}

    for q in data.get("questions", []):
        question_id = q["question_id"]
        row = existing.get(question_id)
        if row:
            row.type = q["type"]
            row.instruction_label = q["instruction_label"]
            row.skill_id = q["skill_id"]
            row.skill_name = q["skill_name"]
            row.difficulty = q["difficulty"]
            row.purpose = q["purpose"]
            row.prompt = q.get("prompt")
            row.options = q.get("options")
            row.correct_option_id = q["correct_option_id"]
            row.explanation = q.get("explanation")
        else:
            session.add(
                Question(
                    question_id=question_id,
                    type=q["type"],
                    instruction_label=q["instruction_label"],
                    skill_id=q["skill_id"],
                    skill_name=q["skill_name"],
                    difficulty=q["difficulty"],
                    purpose=q["purpose"],
                    prompt=q.get("prompt"),
                    options=q.get("options"),
                    correct_option_id=q["correct_option_id"],
                    explanation=q.get("explanation"),
                )
            )

    await session.commit()


async def seed_placement_tests(session: AsyncSession) -> None:
    """Seed 6 bộ đề khảo sát (theo khối lớp x độ khó) từ test-sets.json."""
    data = _load_json("test-sets.json")

    # Map question_id (VD "gsq_001") -> Question.id trong DB
    q_map: dict[str, int] = {}
    q_result = await session.execute(select(Question))
    for q in q_result.scalars().all():
        q_map[q.question_id] = q.id

    existing_result = await session.execute(select(PlacementTest))
    existing = {t.test_id: t for t in existing_result.scalars().all()}

    for test_set in data.get("test_sets", []):
        test_id = test_set["test_id"]
        test = existing.get(test_id)
        if test:
            test.title = test_set["title"]
            test.mascot = test_set.get("mascot")
            test.steps = test_set.get("steps")
            test.levels = [
                {
                    "level_id": test_set["difficulty"],
                    "label": test_set["title"],
                    "grade": test_set["grade"],
                }
            ]
            test.adaptive_config = {
                "strategy": "level_sequential",
                "grade": test_set["grade"],
                "difficulty": test_set["difficulty"],
            }
            await session.flush()
        else:
            test = PlacementTest(
                test_id=test_id,
                title=test_set["title"],
                mascot=test_set.get("mascot"),
                steps=test_set.get("steps"),
                levels=[
                    {
                        "level_id": test_set["difficulty"],
                        "label": test_set["title"],
                        "grade": test_set["grade"],
                    }
                ],
                adaptive_config={
                    "strategy": "level_sequential",
                    "grade": test_set["grade"],
                    "difficulty": test_set["difficulty"],
                },
            )
            session.add(test)
            await session.flush()

        await session.execute(delete(PlacementTestQuestion).where(PlacementTestQuestion.test_id == test.id))

        for order_num, question_id in enumerate(test_set.get("question_ids", []), start=1):
            q_db_id = q_map.get(question_id)
            if not q_db_id:
                continue
            session.add(
                PlacementTestQuestion(
                    test_id=test.id,
                    question_id=q_db_id,
                    order_num=order_num,
                )
            )

    await session.commit()


async def seed_test_results(session: AsyncSession) -> None:
    """Seed student test results from survey-results.json."""
    result = await session.execute(select(StudentTestResult).limit(1))
    if result.scalars().first():
        return

    data = _load_json("survey-results.json")

    # Map email -> User.id
    student_map: dict[str, int] = {}
    s_result = await session.execute(select(User))
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
            user_id=student_id,
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
