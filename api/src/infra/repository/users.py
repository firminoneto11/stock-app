from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.ports import UsersRepoPort
from src.domain.models import User


@dataclass
class UsersRepo(UsersRepoPort):
    session: AsyncSession

    async def get_by_id(self, id: int | str):
        if isinstance(id, int):
            stmt = select(User).where(User.id == id)  # pragma: no cover
        else:
            stmt = select(User).where(User.uuid == id)

        return (await self.session.scalars(stmt)).first()

    async def get_by_username(self, username: str):
        stmt = select(User).where(User.username == username)
        return (await self.session.scalars(stmt)).first()

    async def create(self, username: str, hashed_password: str, is_superuser: bool):
        instance = User(
            username=username,
            password=hashed_password,
            is_superuser=is_superuser,
        )
        self.session.add(instance=instance)
        await self.session.flush()
        return instance
