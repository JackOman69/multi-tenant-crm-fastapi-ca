from datetime import date, datetime
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import Role, TaskModel
from src.domain.exceptions import AuthorizationError, NotFoundError, ValidationError
from src.repositories.deal import DealRepository
from src.repositories.task import TaskRepository
from src.services.permission import PermissionService


class TaskService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.task_repo = TaskRepository(session)
        self.deal_repo = DealRepository(session)

    async def create_task(
        self,
        deal_id: UUID,
        organization_id: UUID,
        user_id: UUID,
        role: Role,
        title: str,
        due_date: date,
        description: str | None = None,
    ) -> TaskModel:
        deal = await self.deal_repo.get_by_id(deal_id)
        if not deal:
            raise NotFoundError("Deal not found")
        if deal.organization_id != organization_id:
            raise NotFoundError("Deal not found")

        if not PermissionService.check_resource_permission(user_id, deal.owner_id, role):
            raise AuthorizationError("Access denied")

        if role == Role.MEMBER and user_id != deal.owner_id:
            raise AuthorizationError("Members can only create tasks for their own deals")

        if due_date < datetime.now().date():
            raise ValidationError("Due date cannot be in the past")

        task = TaskModel(
            id=uuid4(),
            deal_id=deal_id,
            title=title,
            description=description,
            due_date=due_date,
            is_done=False,
        )
        return await self.task_repo.create(task)

    async def list_tasks(
        self,
        organization_id: UUID,
        deal_id: UUID | None = None,
        only_open: bool = False,
    ) -> list[TaskModel]:
        if deal_id:
            deal = await self.deal_repo.get_by_id(deal_id)
            if not deal or deal.organization_id != organization_id:
                raise NotFoundError("Deal not found")
            return await self.task_repo.list_by_deal(deal_id, only_open)
        return []

    async def update_task(
        self,
        task_id: UUID,
        organization_id: UUID,
        user_id: UUID,
        role: Role,
        title: str | None = None,
        description: str | None = None,
        due_date: date | None = None,
        is_done: bool | None = None,
    ) -> TaskModel:
        task = await self.task_repo.get_by_id(task_id)
        if not task:
            raise NotFoundError("Task not found")

        deal = await self.deal_repo.get_by_id(task.deal_id)
        if not deal:
            raise NotFoundError("Deal not found")
        if deal.organization_id != organization_id:
            raise NotFoundError("Task not found")

        if not PermissionService.check_resource_permission(user_id, deal.owner_id, role):
            raise AuthorizationError("Access denied")

        if title is not None:
            task.title = title
        if description is not None:
            task.description = description
        if due_date is not None:
            task.due_date = due_date
        if is_done is not None:
            task.is_done = is_done

        return await self.task_repo.update(task)

    async def get_task(
        self,
        task_id: UUID,
        organization_id: UUID,
    ) -> TaskModel:
        task = await self.task_repo.get_by_id(task_id)
        if not task:
            raise NotFoundError("Task not found")
        deal = await self.deal_repo.get_by_id(task.deal_id)
        if not deal or deal.organization_id != organization_id:
            raise NotFoundError("Task not found")
        return task

    async def delete_task(
        self,
        task_id: UUID,
        organization_id: UUID,
        user_id: UUID,
        role: Role,
    ) -> None:
        task = await self.task_repo.get_by_id(task_id)
        if not task:
            raise NotFoundError("Task not found")
        deal = await self.deal_repo.get_by_id(task.deal_id)
        if not deal:
            raise NotFoundError("Deal not found")
        if deal.organization_id != organization_id:
            raise NotFoundError("Task not found")
        if not PermissionService.check_resource_permission(user_id, deal.owner_id, role):
            raise AuthorizationError("Access denied")
        await self.task_repo.delete(task)
