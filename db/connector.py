"""PostgreSQL Connector — fallback to SQLite when PostgreSQL is unavailable."""
import os
from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy import select

from db.models import Base, Role

DATABASE_URL = os.environ.get("DATABASE_URL", "")

if not DATABASE_URL:
    DATABASE_URL = "sqlite+aiosqlite:///./vnexus.db"

engine = create_async_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_session() -> AsyncIterator[AsyncSession]:
    async with SessionLocal() as session:
        yield session


async def init_db() -> None:
    """Khởi tạo cấu trúc bảng và seed dữ liệu."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with SessionLocal() as session:
        async with session.begin():
            result = await session.execute(select(Role).limit(1))
            if not result.scalars().first():
                roles = [
                    Role(id=1, name="hoc_sinh", description="Hoc sinh"),
                    Role(id=2, name="giao_vien", description="Giao vien"),
                    Role(id=3, name="admin", description="Admin"),
                ]
                session.add_all(roles)

    from db.seed import seed_data
    from db.seed_data import seed_skills, seed_questions_from_json, seed_sample_data

    async with SessionLocal() as session:
        await seed_data(session)
        await seed_skills(session)
        await seed_questions_from_json(session)
        await seed_sample_data(session)
        await session.commit()
