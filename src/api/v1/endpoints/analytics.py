from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_organization_context
from src.api.v1.schemas.analytics import DealSummaryResponse, FunnelResponse
from src.db.models import OrganizationMemberModel
from src.db.session import get_db
from src.services.analytics import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get(
    "/deals/summary",
    response_model=DealSummaryResponse,
    summary="Сводка по сделкам",
    description="Возвращает агрегированную статистику по сделкам: количество, суммы, средние значения.",
)
async def get_deals_summary(
    org_context: tuple[UUID, OrganizationMemberModel] = Depends(get_organization_context),
    session: AsyncSession = Depends(get_db),
) -> DealSummaryResponse:
    org_id, member = org_context
    analytics_service = AnalyticsService(session)

    summary = await analytics_service.get_deals_summary(org_id)
    return DealSummaryResponse(**summary)


@router.get(
    "/deals/funnel",
    response_model=FunnelResponse,
    summary="Воронка продаж",
    description="Возвращает распределение сделок по стадиям воронки.",
)
async def get_deals_funnel(
    org_context: tuple[UUID, OrganizationMemberModel] = Depends(get_organization_context),
    session: AsyncSession = Depends(get_db),
) -> FunnelResponse:
    org_id, member = org_context
    analytics_service = AnalyticsService(session)

    funnel = await analytics_service.get_deals_funnel(org_id)
    return FunnelResponse(stages=funnel)
