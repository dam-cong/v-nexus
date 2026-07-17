"""Seed demo data for V-Nexus Tutor."""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Student, Teacher, Ranking
from db.password import hash_password


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
