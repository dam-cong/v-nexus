"""PostgreSQL Connector dùng chung cho toàn bộ dự án."""
import os
from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy import select

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


async def init_db() -> None:
    """Khởi tạo cấu trúc bảng trong CSDL và thêm các vai trò mặc định."""
    # 1. Tạo tất cả các bảng
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

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
