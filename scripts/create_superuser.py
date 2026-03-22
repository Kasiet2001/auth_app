import asyncio
from getpass import getpass

from core.auth import hash_password
from db.session import async_session_maker
from sqlalchemy import select

from models.models import (
    Role,
    User,
)


async def create_superuser():
    email = input("Enter your email: ")
    password = getpass("Enter your password: ")

    async with async_session_maker() as session:
        result = await session.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        if user:
            print("User already exists")
            return
        superuser = User(
            email=email,
            password=hash_password(password),
            role=Role.SUPERUSER,
            first_name="Super",
            last_name="Super",
            is_active=True,
        )
        session.add(superuser)
        await session.commit()
        print("Superuser created successfully")

if __name__ == "__main__":
    asyncio.run(create_superuser())