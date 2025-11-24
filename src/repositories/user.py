from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import UserModel
from src.domain.entities.user import User
from src.repositories.base import BaseRepository


class UserRepository(BaseRepository[UserModel, User]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, UserModel)

    async def get_by_email(self, email: str) -> UserModel | None:
        result = await self.session.execute(select(UserModel).where(UserModel.email == email))
        return result.scalar_one_or_none()
