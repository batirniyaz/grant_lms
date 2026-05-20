from auth.model import User, UserRole, Admin
from auth.util import get_password_hash
from db.get_db import async_session_maker
from sqlalchemy.future import select


async def create_superuser():

    async with async_session_maker() as session:
        async with session.begin():
            result = await session.execute(select(User).filter_by(email='admin@example.com'))
            superuser = result.scalars().first()

            if not superuser:
                # create base user
                user = User(
                    phone="+998999999999",
                    email="admin@example.com",
                    first_name="Super",
                    last_name="User",
                    father_name="Adminovich",
                    hashed_password=get_password_hash("admin"),
                    role=UserRole.ADMIN,
                )
                session.add(user)
                await session.flush()

                # create admin extension with super flag
                admin_row = Admin(user_id=user.id, is_superadmin=True)
                session.add(admin_row)
                await session.commit()