from typing import Any
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import ActivityModel, ActivityType
from src.domain.exceptions import AuthorizationError, NotFoundError
from src.repositories.activity import ActivityRepository
from src.repositories.deal import DealRepository
from src.services.permission import PermissionService


class ActivityService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.activity_repo = ActivityRepository(session)
        self.deal_repo = DealRepository(session)

    async def create_activity(
        self, deal_id: UUID, organization_id: UUID, user_id: UUID, role, content: str
    ) -> ActivityModel:
        deal = await self.deal_repo.get_by_id(deal_id)
        if not deal:
            raise NotFoundError("Deal not found")
        if deal.organization_id != organization_id:
            raise NotFoundError("Deal not found")

        if not PermissionService.check_resource_permission(user_id, deal.owner_id, role):
            raise AuthorizationError("Access denied")

        activity = ActivityModel(
            id=uuid4(),
            deal_id=deal_id,
            author_id=user_id,
            type=ActivityType.COMMENT,
            payload={"content": content},
        )
        return await self.activity_repo.create(activity)

    async def create_system_activity(
        self, deal_id: UUID, activity_type: ActivityType, payload: dict[str, Any]
    ) -> ActivityModel:
        activity = ActivityModel(
            id=uuid4(),
            deal_id=deal_id,
            author_id=None,
            type=activity_type,
            payload=payload,
        )
        return await self.activity_repo.create(activity)

    async def list_activities(
        self, deal_id: UUID, organization_id: UUID, user_id: UUID, role
    ) -> list[ActivityModel]:
        deal = await self.deal_repo.get_by_id(deal_id)
        if not deal:
            raise NotFoundError("Deal not found")
        if deal.organization_id != organization_id:
            raise NotFoundError("Deal not found")

        if not PermissionService.check_resource_permission(user_id, deal.owner_id, role):
            raise AuthorizationError("Access denied")

        return await self.activity_repo.list_by_deal(deal_id)
