from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import ActivityModel
from src.domain.entities.activity import Activity
from src.repositories.base import BaseRepository


class ActivityRepository(BaseRepository[ActivityModel, Activity]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, ActivityModel)

    async def list_by_deal(self, deal_id: UUID) -> list[ActivityModel]:
        result = await self.session.execute(
            select(ActivityModel)
            .where(ActivityModel.deal_id == deal_id)
            .order_by(ActivityModel.created_at.desc())
        )
        return list(result.scalars().all())
