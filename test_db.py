import asyncio, json
from db.connector import async_session_maker
from db.models import StudentTestResult
from sqlalchemy import select
async def run():
    async with async_session_maker() as s:
        r = await s.execute(select(StudentTestResult).where(StudentTestResult.id==18))
        obj = r.scalar_one()
        print('DB training_plan length:', len(obj.training_plan) if obj.training_plan else 'None')
asyncio.run(run())
