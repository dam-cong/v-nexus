
import asyncio
from sqlalchemy import select
from db.connector import get_session
from db.models import StudentTestResult, User

async def check():
    async for db in get_session():
        res = await db.execute(select(StudentTestResult).order_by(StudentTestResult.created_at.desc()))
        results = res.scalars().all()
        print("--- TEST RESULTS ---")
        for r in results:
            # Get user name
            u_res = await db.execute(select(User).where(User.id == r.user_id))
            u = u_res.scalar_one_or_none()
            user_name = u.name if u else "Unknown"
            print(f"ID: {r.id}, User ID: {r.user_id} ({user_name}), Test ID: {r.test_id}, Date: {r.test_date}")

asyncio.run(check())
