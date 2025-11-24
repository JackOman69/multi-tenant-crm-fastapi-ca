from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_organization_context
from src.api.v1.schemas.contact import (
    ContactCreate,
    ContactListResponse,
    ContactResponse,
    ContactUpdate,
)
from src.db.models import OrganizationMemberModel
from src.db.session import get_db
from src.domain.exceptions import AuthorizationError, ConflictError, NotFoundError
from src.services.contact import ContactService

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.get(
    "",
    response_model=ContactListResponse,
    summary="Список контактов",
    description="Возвращает список контактов организации с пагинацией и поиском.",
)
async def list_contacts(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    search: str | None = Query(None),
    org_context: tuple[UUID, OrganizationMemberModel] = Depends(get_organization_context),
    session: AsyncSession = Depends(get_db),
) -> ContactListResponse:
    org_id, member = org_context
    contact_service = ContactService(session)

    contacts, total = await contact_service.list_contacts(
        organization_id=org_id,
        limit=limit,
        offset=offset,
        search=search,
    )

    return ContactListResponse(
        items=[ContactResponse.model_validate(c) for c in contacts],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.post(
    "",
    response_model=ContactResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создание контакта",
    description="Создаёт новый контакт в организации. Текущий пользователь становится владельцем контакта.",
)
async def create_contact(
    request: ContactCreate,
    org_context: tuple[UUID, OrganizationMemberModel] = Depends(get_organization_context),
    session: AsyncSession = Depends(get_db),
) -> ContactResponse:
    org_id, member = org_context
    contact_service = ContactService(session)

    contact = await contact_service.create_contact(
        organization_id=org_id,
        owner_id=member.user_id,
        name=request.name,
        email=request.email,
        phone=request.phone,
    )

    return ContactResponse.model_validate(contact)


@router.get(
    "/{contact_id}",
    response_model=ContactResponse,
    summary="Получение контакта",
    description="Возвращает детальную информацию о контакте по его ID.",
)
async def get_contact(
    contact_id: UUID,
    org_context: tuple[UUID, OrganizationMemberModel] = Depends(get_organization_context),
    session: AsyncSession = Depends(get_db),
) -> ContactResponse:
    org_id, member = org_context
    contact_service = ContactService(session)

    try:
        contact = await contact_service.get_contact(contact_id, org_id)
        return ContactResponse.model_validate(contact)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.patch(
    "/{contact_id}",
    response_model=ContactResponse,
    summary="Обновление контакта",
    description="Обновляет данные контакта. Только владелец контакта или администраторы могут вносить изменения.",
)
async def update_contact(
    contact_id: UUID,
    request: ContactUpdate,
    org_context: tuple[UUID, OrganizationMemberModel] = Depends(get_organization_context),
    session: AsyncSession = Depends(get_db),
) -> ContactResponse:
    org_id, member = org_context
    contact_service = ContactService(session)

    try:
        contact = await contact_service.update_contact(
            contact_id=contact_id,
            user_id=member.user_id,
            user_role=member.role,
            name=request.name,
            email=request.email,
            phone=request.phone,
        )
        return ContactResponse.model_validate(contact)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except AuthorizationError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.delete(
    "/{contact_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удаление контакта",
    description="Удаляет контакт из системы. Нельзя удалить контакт, если у него есть активные сделки.",
)
async def delete_contact(
    contact_id: UUID,
    org_context: tuple[UUID, OrganizationMemberModel] = Depends(get_organization_context),
    session: AsyncSession = Depends(get_db),
) -> None:
    org_id, member = org_context
    contact_service = ContactService(session)

    try:
        await contact_service.delete_contact(
            contact_id=contact_id,
            user_id=member.user_id,
            user_role=member.role,
        )
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except AuthorizationError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ConflictError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
