from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_organization_context
from src.api.v1.schemas.task import TaskCreate, TaskListResponse, TaskResponse, TaskUpdate
from src.db.models import OrganizationMemberModel
from src.db.session import get_db
from src.domain.exceptions import AuthorizationError, NotFoundError, ValidationError
from src.services.task import TaskService

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get(
    "",
    response_model=TaskListResponse,
    summary="Список задач",
    description="Возвращает список задач с возможностью фильтрации по сделке и статусу выполнения.",
)
async def list_tasks(
    deal_id: UUID | None = Query(None),
    only_open: bool = Query(False),
    org_context: tuple[UUID, OrganizationMemberModel] = Depends(get_organization_context),
    session: AsyncSession = Depends(get_db),
) -> TaskListResponse:
    org_id, member = org_context
    task_service = TaskService(session)

    tasks = await task_service.list_tasks(
        organization_id=org_id,
        deal_id=deal_id,
        only_open=only_open,
    )

    return TaskListResponse(items=[TaskResponse.model_validate(t) for t in tasks])


@router.post(
    "",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создание задачи",
    description="Создаёт новую задачу для сделки. Автоматически добавляется запись в историю активностей сделки.",
)
async def create_task(
    deal_id: UUID,
    request: TaskCreate,
    org_context: tuple[UUID, OrganizationMemberModel] = Depends(get_organization_context),
    session: AsyncSession = Depends(get_db),
) -> TaskResponse:
    org_id, member = org_context
    task_service = TaskService(session)

    try:
        task = await task_service.create_task(
            deal_id=deal_id,
            organization_id=org_id,
            user_id=member.user_id,
            role=member.role,
            title=request.title,
            description=request.description,
            due_date=request.due_date,
        )
        return TaskResponse.model_validate(task)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except AuthorizationError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Получение задачи",
    description="Возвращает детальную информацию о задаче по её ID.",
)
async def get_task(
    task_id: UUID,
    org_context: tuple[UUID, OrganizationMemberModel] = Depends(get_organization_context),
    session: AsyncSession = Depends(get_db),
) -> TaskResponse:
    org_id, member = org_context
    task_service = TaskService(session)

    try:
        task = await task_service.get_task(task_id, org_id)
        return TaskResponse.model_validate(task)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.patch(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Обновление задачи",
    description="Обновляет данные задачи: название, описание, срок выполнения или статус завершения.",
)
async def update_task(
    task_id: UUID,
    request: TaskUpdate,
    org_context: tuple[UUID, OrganizationMemberModel] = Depends(get_organization_context),
    session: AsyncSession = Depends(get_db),
) -> TaskResponse:
    org_id, member = org_context
    task_service = TaskService(session)

    try:
        task = await task_service.update_task(
            task_id=task_id,
            organization_id=org_id,
            user_id=member.user_id,
            role=member.role,
            title=request.title,
            description=request.description,
            due_date=request.due_date,
            is_done=request.is_done,
        )
        return TaskResponse.model_validate(task)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except AuthorizationError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удаление задачи",
    description="Удаляет задачу из системы. Только владелец сделки или администраторы могут удалять задачи.",
)
async def delete_task(
    task_id: UUID,
    org_context: tuple[UUID, OrganizationMemberModel] = Depends(get_organization_context),
    session: AsyncSession = Depends(get_db),
) -> None:
    org_id, member = org_context
    task_service = TaskService(session)

    try:
        await task_service.delete_task(
            task_id=task_id,
            organization_id=org_id,
            user_id=member.user_id,
            role=member.role,
        )
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except AuthorizationError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
