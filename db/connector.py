"""PostgreSQL Connector dùng chung cho toàn bộ dự án."""
import os
from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy import select, text

from db.models import Base, Role
from db.seed import seed_data, seed_questions, seed_placement_tests, seed_test_results

DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql+asyncpg://vnexus:vnexus@localhost:5432/vnexus"
)

# Use pool_pre_ping to check connection and avoid stale connections
engine = create_async_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_session() -> AsyncIterator[AsyncSession]:
    async with SessionLocal() as session:
        yield session


async def migrate_to_users() -> None:
    """Gộp students/teachers cũ vào bảng users trung tâm (chạy 1 lần, idempotent).

    Bước:
      1. Nếu bảng users đã có dữ liệu -> bỏ qua (đã migrate).
      2. Nếu students/teachers cũ rỗng -> bỏ qua (chưa có data).
      3. Với mỗi student/teacher cũ: tạo User, gán user_id vào profile.
      4. Map old student.id/teacher.id -> user.id, cập nhật rankings/student_test_results.
    """
    async with SessionLocal() as session:
        # Check users already migrated
        users_exist = await session.execute(text("SELECT 1 FROM users LIMIT 1"))
        if users_exist.first() is not None:
            return

        # Detect legacy schema: old students/teachers had a `name` column.
        # On a fresh DB (new schema) those columns don't exist -> skip migration.
        legacy_cols = await session.execute(text(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name = 'students' AND column_name = 'name'"
        ))
        if legacy_cols.first() is None:
            return

        # Old students/teachers
        old_students = (await session.execute(text(
            "SELECT id, name, email, hashed_password, role_id, grade "
            "FROM students WHERE user_id IS NULL"
        ))).fetchall()
        old_teachers = (await session.execute(text(
            "SELECT id, name, email, hashed_password, role_id, subject "
            "FROM teachers WHERE user_id IS NULL"
        ))).fetchall()

        if not old_students and not old_teachers:
            return

        # Map old profile id -> new user id
        id_map = {}  # (table, old_id) -> user_id

        for row in old_students:
            sid, name, email, hp, role_id, grade = row
            res = await session.execute(
                text(
                    "INSERT INTO users (name, email, hashed_password, role_id, created_at) "
                    "VALUES (:name, :email, :hp, :role, now()) RETURNING id"
                ),
                {"name": name, "email": email, "hp": hp, "role": role_id or 1},
            )
            uid = res.scalar_one()
            id_map[("students", sid)] = uid
            await session.execute(
                text("UPDATE students SET user_id = :uid WHERE id = :sid"),
                {"uid": uid, "sid": sid},
            )

        for row in old_teachers:
            tid, name, email, hp, role_id, subject = row
            res = await session.execute(
                text(
                    "INSERT INTO users (name, email, hashed_password, role_id, created_at) "
                    "VALUES (:name, :email, :hp, :role, now()) RETURNING id"
                ),
                {"name": name, "email": email, "hp": hp, "role": role_id or 2},
            )
            uid = res.scalar_one()
            id_map[("teachers", tid)] = uid
            await session.execute(
                text("UPDATE teachers SET user_id = :uid WHERE id = :tid"),
                {"uid": uid, "tid": tid},
            )

        # Update rankings: cột student_id cũ -> user_id
        rank_rows = (await session.execute(text(
            "SELECT id, student_id FROM rankings WHERE user_id IS NULL"
        ))).fetchall()
        for rid, student_id in rank_rows:
            uid = id_map.get(("students", student_id))
            if uid:
                await session.execute(
                    text("UPDATE rankings SET user_id = :uid WHERE id = :rid"),
                    {"uid": uid, "rid": rid},
                )

        # Update student_test_results: cột student_id cũ -> user_id
        str_rows = (await session.execute(text(
            "SELECT id, student_id FROM student_test_results WHERE user_id IS NULL"
        ))).fetchall()
        for trid, student_id in str_rows:
            uid = id_map.get(("students", student_id))
            if uid:
                await session.execute(
                    text("UPDATE student_test_results SET user_id = :uid WHERE id = :trid"),
                    {"uid": uid, "trid": trid},
                )

        await session.commit()


async def init_db() -> None:
    """Khởi tạo cấu trúc bảng trong CSDL và thêm các vai trò mặc định."""
    # 1. Tạo tất cả các bảng
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # 1b. Thêm cột mới nếu chưa tồn tại (tương đương migration nhẹ, không dùng Alembic)
    async with engine.begin() as conn:
        await conn.execute(
            text(
                "ALTER TABLE student_test_results "
                "ADD COLUMN IF NOT EXISTS training_plan TEXT;"
            )
        )
        await conn.execute(
            text(
                "ALTER TABLE student_test_results "
                "ADD COLUMN IF NOT EXISTS roadmap_completed BOOLEAN DEFAULT FALSE;"
            )
        )
        await conn.execute(
            text(
                "ALTER TABLE student_test_results "
                "ADD COLUMN IF NOT EXISTS quick_check_passed BOOLEAN DEFAULT FALSE;"
            )
        )
        await conn.execute(
            text(
                "ALTER TABLE students ADD COLUMN IF NOT EXISTS user_id INTEGER;"
            )
        )
        await conn.execute(
            text(
                "ALTER TABLE students ADD COLUMN IF NOT EXISTS years_studying_english INTEGER;"
            )
        )
        await conn.execute(
            text(
                "ALTER TABLE students ADD COLUMN IF NOT EXISTS learning_environment VARCHAR(50);"
            )
        )
        await conn.execute(
            text(
                "ALTER TABLE students ADD COLUMN IF NOT EXISTS self_assessment_level VARCHAR(50);"
            )
        )
        await conn.execute(
            text(
                "ALTER TABLE students ADD COLUMN IF NOT EXISTS learning_goal TEXT;"
            )
        )
        await conn.execute(
            text(
                "ALTER TABLE students ADD COLUMN IF NOT EXISTS training_plan TEXT;"
            )
        )
        await conn.execute(
            text(
                "ALTER TABLE teachers ADD COLUMN IF NOT EXISTS user_id INTEGER;"
            )
        )
        await conn.execute(
            text(
                "ALTER TABLE rankings ADD COLUMN IF NOT EXISTS user_id INTEGER;"
            )
        )
        await conn.execute(
            text(
                "ALTER TABLE student_test_results ADD COLUMN IF NOT EXISTS user_id INTEGER;"
            )
        )
        # Drop old NOT NULL columns after migration (only if still present)
        await conn.execute(text("ALTER TABLE student_test_results DROP COLUMN IF EXISTS student_id;"))
        await conn.execute(text("ALTER TABLE rankings DROP COLUMN IF EXISTS student_id;"))
        # Drop legacy duplicated columns on profile tables (data now lives in users)
        await conn.execute(text("ALTER TABLE students DROP COLUMN IF EXISTS student_id;"))
        await conn.execute(text("ALTER TABLE students DROP COLUMN IF EXISTS name;"))
        await conn.execute(text("ALTER TABLE students DROP COLUMN IF EXISTS email;"))
        await conn.execute(text("ALTER TABLE students DROP COLUMN IF EXISTS hashed_password;"))
        await conn.execute(text("ALTER TABLE students DROP COLUMN IF EXISTS role_id;"))
        await conn.execute(text("ALTER TABLE teachers DROP COLUMN IF EXISTS teacher_id;"))
        await conn.execute(text("ALTER TABLE teachers DROP COLUMN IF EXISTS name;"))
        await conn.execute(text("ALTER TABLE teachers DROP COLUMN IF EXISTS email;"))
        await conn.execute(text("ALTER TABLE teachers DROP COLUMN IF EXISTS hashed_password;"))
        await conn.execute(text("ALTER TABLE teachers DROP COLUMN IF EXISTS role_id;"))

    # 1c. Migrate dữ liệu cũ (students/teachers riêng) sang mô hình users + profile
    await migrate_to_users()

    # 2. Thêm các vai trò mặc định nếu chưa tồn tại
    async with SessionLocal() as session:
        async with session.begin():
            result = await session.execute(select(Role).limit(1))
            if not result.scalars().first():
                roles = [
                    Role(id=1, name="hoc_sinh", description="Học sinh tham gia học tập"),
                    Role(id=2, name="giao_vien", description="Giáo viên quản lý và giảng dạy"),
                    Role(id=3, name="admin", description="Quản trị viên hệ thống"),
                ]
                session.add_all(roles)

    # 3. Seed demo data
    async with SessionLocal() as session:
        async with session.begin():
            await seed_data(session)

    # 4. Seed questions, placement tests, and test results
    async with SessionLocal() as session:
        async with session.begin():
            await seed_questions(session)

    async with SessionLocal() as session:
        async with session.begin():
            await seed_placement_tests(session)

    async with SessionLocal() as session:
        async with session.begin():
            await seed_test_results(session)
