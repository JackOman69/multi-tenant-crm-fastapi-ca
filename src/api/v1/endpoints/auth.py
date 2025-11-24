from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.v1.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    RegisterResponse,
    TokenResponse,
)
from src.db.session import get_db
from src.domain.exceptions import AuthenticationError, ConflictError
from src.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация нового пользователя",
    description="Создаёт нового пользователя и организацию. Пользователь автоматически становится owner организации. Для получения токенов используйте /login.",
)
async def register(
    request: RegisterRequest,
    session: AsyncSession = Depends(get_db),
) -> RegisterResponse:
    auth_service = AuthService(session)
    try:
        user, org = await auth_service.register(
            email=request.email,
            password=request.password,
            name=request.name,
            org_name=request.organization_name,
        )
        return RegisterResponse(
            id=str(user.id),
            email=user.email,
            name=user.name,
            organization_id=str(org.id),
            organization_name=org.name,
        )
    except ConflictError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Вход в систему",
    description="Аутентификация пользователя по email и паролю. Возвращает access и refresh токены.",
)
async def login(
    request: LoginRequest,
    session: AsyncSession = Depends(get_db),
) -> TokenResponse:
    auth_service = AuthService(session)
    try:
        tokens = await auth_service.login(email=request.email, password=request.password)
        return TokenResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
        )
    except AuthenticationError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
