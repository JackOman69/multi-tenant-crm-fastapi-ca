from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import TaskModel
from src.domain.entities.task import Task
from src.repositories.base import BaseRepository


class TaskRepository(BaseRepository[TaskModel, Task]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, TaskModel)

    async def list_by_deal(
        self, deal_id: UUID, only_open: bool = False
    ) -> list[TaskModel]:
        query = select(TaskModel).where(TaskModel.deal_id == deal_id)

        if only_open:
            query = query.where(~TaskModel.is_done)

        query = query.order_by(TaskModel.due_date)
        result = await self.session.execute(query)
        return list(result.scalars().all())
