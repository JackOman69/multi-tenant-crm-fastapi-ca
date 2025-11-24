from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import ActivityType, DealModel, DealStage, DealStatus
from src.domain.exceptions import AuthorizationError, NotFoundError, ValidationError
from src.repositories.contact import ContactRepository
from src.repositories.deal import DealRepository
from src.services.activity import ActivityService
from src.services.permission import PermissionService


class DealService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.deal_repo = DealRepository(session)
        self.contact_repo = ContactRepository(session)
        self.activity_service = ActivityService(session)

    async def create_deal(
        self,
        organization_id: UUID,
        contact_id: UUID,
        owner_id: UUID,
        title: str,
        amount: Decimal,
        currency: str = "USD",
    ) -> DealModel:
        contact = await self.contact_repo.get_by_id(contact_id)
        if not contact:
            raise NotFoundError("Contact not found")

        if contact.organization_id != organization_id:
            raise ValidationError("Contact does not belong to organization")

        deal = DealModel(
            id=uuid4(),
            organization_id=organization_id,
            contact_id=contact_id,
            owner_id=owner_id,
            title=title,
            amount=amount,
            currency=currency,
            status=DealStatus.NEW,
            stage=DealStage.QUALIFICATION,
        )
        return await self.deal_repo.create(deal)

    async def list_deals(
        self,
        organization_id: UUID,
        limit: int = 50,
        offset: int = 0,
        status: DealStatus | None = None,
        stage: DealStage | None = None,
        owner_id: UUID | None = None,
    ) -> tuple[list[DealModel], int]:
        return await self.deal_repo.list_by_organization(
            organization_id, limit, offset, status, stage, owner_id
        )

    async def update_deal(
        self,
        deal_id: UUID,
        organization_id: UUID,
        user_id: UUID,
        user_role,
        title: str | None = None,
        amount: Decimal | None = None,
        status: DealStatus | None = None,
        stage: DealStage | None = None,
    ) -> DealModel:
        deal = await self.deal_repo.get_by_id(deal_id)
        if not deal or deal.organization_id != organization_id:
            raise NotFoundError("Deal not found")

        if not PermissionService.check_resource_permission(user_id, deal.owner_id, user_role):
            raise AuthorizationError("Access denied")

        if stage and stage != deal.stage:
            if not PermissionService.can_rollback_stage(user_role, deal.stage, stage):
                raise AuthorizationError("Cannot rollback stage")

            await self.activity_service.create_system_activity(
                deal_id, ActivityType.STAGE_CHANGED,
                {"old_stage": deal.stage, "new_stage": stage}
            )
            deal.stage = stage

        if status and status != deal.status:
            if status == DealStatus.WON and deal.amount <= 0:
                raise ValidationError("Won deal must have positive amount")

            await self.activity_service.create_system_activity(
                deal_id, ActivityType.STATUS_CHANGED,
                {"old_status": deal.status, "new_status": status}
            )
            deal.status = status

        if title:
            deal.title = title
        if amount:
            deal.amount = amount

        return await self.deal_repo.update(deal)

    async def get_deal(
        self,
        deal_id: UUID,
        organization_id: UUID,
    ) -> DealModel:
        deal = await self.deal_repo.get_by_id(deal_id)
        if not deal:
            raise NotFoundError("Deal not found")
        if deal.organization_id != organization_id:
            raise NotFoundError("Deal not found")
        return deal

    async def delete_deal(
        self,
        deal_id: UUID,
        organization_id: UUID,
        user_id: UUID,
        role,
    ) -> None:
        deal = await self.deal_repo.get_by_id(deal_id)
        if not deal or deal.organization_id != organization_id:
            raise NotFoundError("Deal not found")

        if not PermissionService.check_resource_permission(user_id, deal.owner_id, role):
            raise AuthorizationError("Access denied")

        await self.deal_repo.delete(deal)
