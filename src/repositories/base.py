from typing import Generic, TypeVar
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.base import Base

ModelType = TypeVar("ModelType", bound=Base)
EntityType = TypeVar("EntityType")


class BaseRepository(Generic[ModelType, EntityType]):
    def __init__(self, session: AsyncSession, model: type[ModelType]):
        self.session = session
        self.model = model

    async def get_by_id(self, id: UUID) -> ModelType | None:
        result = await self.session.execute(select(self.model).where(self.model.id == id))
        return result.scalar_one_or_none()

    async def create(self, model: ModelType) -> ModelType:
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return model

    async def update(self, model: ModelType) -> ModelType:
        await self.session.flush()
        await self.session.refresh(model)
        return model

    async def delete(self, model: ModelType) -> None:
        await self.session.delete(model)
        await self.session.flush()
