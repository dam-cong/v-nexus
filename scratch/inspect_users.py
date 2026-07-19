
import asyncio
from sqlalchemy import select
from db.connector import get_session
from db.models import User, Student, Teacher, Role

async def check():
    async for db in get_session():
        # Get users
        res = await db.execute(select(User))
        users = res.scalars().all()
        print("--- USERS ---")
        for u in users:
            print(f"ID: {u.id}, Name: {u.name}, Email: {u.email}, Role ID: {u.role_id}")
            
        # Get students
        res = await db.execute(select(Student))
        students = res.scalars().all()
        print("--- STUDENTS ---")
        for s in students:
            print(f"ID: {s.id}, User ID: {s.user_id}, Grade: {s.grade}")
            
        # Get teachers
        res = await db.execute(select(Teacher))
        teachers = res.scalars().all()
        print("--- TEACHERS ---")
        for t in teachers:
            print(f"ID: {t.id}, User ID: {t.user_id}, Subject: {t.subject}")

asyncio.run(check())
