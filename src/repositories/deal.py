from decimal import Decimal
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import DealModel, DealStage, DealStatus
from src.domain.entities.deal import Deal
from src.repositories.base import BaseRepository


class DealRepository(BaseRepository[DealModel, Deal]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, DealModel)

    async def list_by_organization(
        self,
        organization_id: UUID,
        limit: int = 50,
        offset: int = 0,
        status: DealStatus | None = None,
        stage: DealStage | None = None,
        owner_id: UUID | None = None,
    ) -> tuple[list[DealModel], int]:
        query = select(DealModel).where(DealModel.organization_id == organization_id)

        if status:
            query = query.where(DealModel.status == status)
        if stage:
            query = query.where(DealModel.stage == stage)
        if owner_id:
            query = query.where(DealModel.owner_id == owner_id)

        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.session.execute(count_query)
        total = total_result.scalar_one()

        query = query.order_by(DealModel.created_at.desc()).limit(limit).offset(offset)
        result = await self.session.execute(query)
        deals = list(result.scalars().all())

        return deals, total

    async def get_summary(self, organization_id: UUID) -> dict[str, int | Decimal]:
        result = await self.session.execute(
            select(
                DealModel.status,
                func.count(DealModel.id).label("count"),
                func.coalesce(func.sum(DealModel.amount), 0).label("total_amount"),
            )
            .where(DealModel.organization_id == organization_id)
            .group_by(DealModel.status)
        )

        summary = {
            "total_count": 0,
            "new_count": 0,
            "in_progress_count": 0,
            "won_count": 0,
            "lost_count": 0,
            "total_amount": Decimal("0"),
            "won_amount": Decimal("0"),
        }

        for row in result:
            status = row.status
            count = row.count
            amount = row.total_amount

            summary["total_count"] += count
            summary["total_amount"] += amount

            if status == DealStatus.NEW:
                summary["new_count"] = count
            elif status == DealStatus.IN_PROGRESS:
                summary["in_progress_count"] = count
            elif status == DealStatus.WON:
                summary["won_count"] = count
                summary["won_amount"] = amount
            elif status == DealStatus.LOST:
                summary["lost_count"] = count

        if summary["won_count"] > 0:
            summary["average_won_amount"] = summary["won_amount"] / summary["won_count"]
        else:
            summary["average_won_amount"] = Decimal("0")

        return summary

    async def get_funnel(self, organization_id: UUID) -> list[dict[str, int | str]]:
        result = await self.session.execute(
            select(DealModel.stage, func.count(DealModel.id).label("count"))
            .where(
                DealModel.organization_id == organization_id,
                DealModel.status.in_([DealStatus.NEW, DealStatus.IN_PROGRESS]),
            )
            .group_by(DealModel.stage)
        )

        funnel = []
        for row in result:
            funnel.append({"stage": row.stage, "count": row.count})

        return funnel
