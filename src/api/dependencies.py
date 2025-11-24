from uuid import UUID

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.security import verify_token
from src.db.models import OrganizationMemberModel, UserModel
from src.db.session import get_db
from src.repositories.organization_member import OrganizationMemberRepository
from src.repositories.user import UserRepository

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_db),
) -> UserModel:
    token = credentials.credentials
    user_id = verify_token(token, "access")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    user_repo = UserRepository(session)
    user = await user_repo.get_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user


async def get_organization_context(
    x_organization_id: str = Header(...),
    user: UserModel = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> tuple[UUID, OrganizationMemberModel]:
    try:
        org_id = UUID(x_organization_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid organization ID format",
        )

    member_repo = OrganizationMemberRepository(session)
    results = await member_repo.get_user_organizations(user.id)

    member = next((m for m, org in results if m.organization_id == org_id), None)

    if not member:
        available_orgs = [str(m.organization_id) for m, org in results]
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied to organization. Available organizations: {available_orgs}",
        )

    return org_id, member
