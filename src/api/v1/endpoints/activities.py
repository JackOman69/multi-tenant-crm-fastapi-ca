from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_organization_context
from src.api.v1.schemas.activity import (
    ActivityCreate,
    ActivityListResponse,
    ActivityResponse,
)
from src.db.models import OrganizationMemberModel
from src.db.session import get_db
from src.domain.exceptions import AuthorizationError, NotFoundError
from src.services.activity import ActivityService

router = APIRouter(prefix="/deals/{deal_id}/activities", tags=["activities"])


@router.get(
    "",
    response_model=ActivityListResponse,
    summary="История активностей",
    description="Возвращает полную историю активностей по сделке: комментарии, изменения статуса и стадии, создание задач.",
)
async def list_activities(
    deal_id: UUID,
    org_context: tuple[UUID, OrganizationMemberModel] = Depends(get_organization_context),
    session: AsyncSession = Depends(get_db),
) -> ActivityListResponse:
    org_id, member = org_context
    activity_service = ActivityService(session)

    try:
        activities = await activity_service.list_activities(
            deal_id=deal_id,
            organization_id=org_id,
            user_id=member.user_id,
            role=member.role,
        )
        return ActivityListResponse(items=[ActivityResponse.model_validate(a) for a in activities])
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except AuthorizationError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.post(
    "",
    response_model=ActivityResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Добавление комментария",
    description="Добавляет комментарий к сделке. Комментарий сохраняется в истории активностей с указанием автора.",
)
async def create_activity(
    deal_id: UUID,
    request: ActivityCreate,
    org_context: tuple[UUID, OrganizationMemberModel] = Depends(get_organization_context),
    session: AsyncSession = Depends(get_db),
) -> ActivityResponse:
    org_id, member = org_context
    activity_service = ActivityService(session)

    try:
        activity = await activity_service.create_activity(
            deal_id=deal_id,
            organization_id=org_id,
            user_id=member.user_id,
            role=member.role,
            content=request.content,
        )
        return ActivityResponse.model_validate(activity)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except AuthorizationError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
