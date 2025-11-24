from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_organization_context
from src.api.v1.schemas.deal import DealCreate, DealListResponse, DealResponse, DealUpdate
from src.db.models import DealStage, DealStatus, OrganizationMemberModel
from src.db.session import get_db
from src.domain.exceptions import AuthorizationError, NotFoundError, ValidationError
from src.services.deal import DealService

router = APIRouter(prefix="/deals", tags=["deals"])


@router.get(
    "",
    response_model=DealListResponse,
    summary="Список сделок",
    description="Возвращает список сделок с фильтрацией по статусу и стадии.",
)
async def list_deals(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    status: DealStatus | None = Query(None),
    stage: DealStage | None = Query(None),
    org_context: tuple[UUID, OrganizationMemberModel] = Depends(get_organization_context),
    session: AsyncSession = Depends(get_db),
) -> DealListResponse:
    org_id, member = org_context
    deal_service = DealService(session)

    deals, total = await deal_service.list_deals(
        organization_id=org_id,
        limit=limit,
        offset=offset,
        status=status,
        stage=stage,
    )

    return DealListResponse(
        items=[DealResponse.model_validate(d) for d in deals],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.post(
    "",
    response_model=DealResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создание сделки",
    description="Создаёт новую сделку для контакта. Начальный статус: NEW, стадия: QUALIFICATION.",
)
async def create_deal(
    request: DealCreate,
    org_context: tuple[UUID, OrganizationMemberModel] = Depends(get_organization_context),
    session: AsyncSession = Depends(get_db),
) -> DealResponse:
    org_id, member = org_context
    deal_service = DealService(session)

    try:
        deal = await deal_service.create_deal(
            organization_id=org_id,
            owner_id=member.user_id,
            contact_id=request.contact_id,
            title=request.title,
            amount=request.amount,
            currency=request.currency,
        )
        return DealResponse.model_validate(deal)
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "/{deal_id}",
    response_model=DealResponse,
    summary="Получение сделки",
    description="Возвращает детальную информацию о сделке по её ID.",
)
async def get_deal(
    deal_id: UUID,
    org_context: tuple[UUID, OrganizationMemberModel] = Depends(get_organization_context),
    session: AsyncSession = Depends(get_db),
) -> DealResponse:
    org_id, member = org_context
    deal_service = DealService(session)

    try:
        deal = await deal_service.get_deal(deal_id, org_id)
        return DealResponse.model_validate(deal)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.patch(
    "/{deal_id}",
    response_model=DealResponse,
    summary="Обновление сделки",
    description="Обновляет данные сделки: название, сумму, статус или стадию. При изменении статуса или стадии автоматически создаётся запись в истории активностей.",
)
async def update_deal(
    deal_id: UUID,
    request: DealUpdate,
    org_context: tuple[UUID, OrganizationMemberModel] = Depends(get_organization_context),
    session: AsyncSession = Depends(get_db),
) -> DealResponse:
    org_id, member = org_context
    deal_service = DealService(session)

    try:
        deal = await deal_service.update_deal(
            deal_id=deal_id,
            organization_id=org_id,
            user_id=member.user_id,
            user_role=member.role,
            title=request.title,
            amount=request.amount,
            status=request.status,
            stage=request.stage,
        )
        return DealResponse.model_validate(deal)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except AuthorizationError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete(
    "/{deal_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удаление сделки",
    description="Удаляет сделку и все связанные с ней задачи и активности. Только владелец сделки или администраторы могут удалять сделки.",
)
async def delete_deal(
    deal_id: UUID,
    org_context: tuple[UUID, OrganizationMemberModel] = Depends(get_organization_context),
    session: AsyncSession = Depends(get_db),
) -> None:
    org_id, member = org_context
    deal_service = DealService(session)

    try:
        await deal_service.delete_deal(
            deal_id=deal_id,
            organization_id=org_id,
            user_id=member.user_id,
            role=member.role,
        )
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except AuthorizationError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
