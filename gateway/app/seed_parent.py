import asyncio
import os
import sys

# Add the project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.future import select

from db.connector import SessionLocal
from db.models import User, Parent, Role
from db.password import hash_password

async def seed_parent():
    async with SessionLocal() as db:
        # Check if role 4 exists, if not create it
        res = await db.execute(select(Role).where(Role.id == 4))
        role = res.scalar_one_or_none()
        if not role:
            role = Role(id=4, name="phu_huynh", description="Phụ huynh học sinh")
            db.add(role)
            await db.commit()

        # Check if parent exists
        res = await db.execute(select(User).where(User.email == "phuhuynh@test.com"))
        user = res.scalar_one_or_none()
        
        if not user:
            user = User(
                name="Phụ Huynh Test",
                email="phuhuynh@test.com",
                hashed_password=hash_password("12345678"),
                role_id=4
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
            
            parent_profile = Parent(
                user_id=user.id,
                phone_number="0123456789"
            )
            db.add(parent_profile)
            await db.commit()
            print(f"Created parent user: phuhuynh@test.com / 12345678 (ID: {user.id})")
        else:
            print(f"Parent user already exists: phuhuynh@test.com / 12345678 (ID: {user.id})")

if __name__ == "__main__":
    asyncio.run(seed_parent())
