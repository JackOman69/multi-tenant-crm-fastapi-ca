from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_current_user
from src.db.models import UserModel
from src.db.session import get_db
from src.repositories.organization_member import OrganizationMemberRepository

router = APIRouter(prefix="/organizations", tags=["organizations"])


@router.get(
    "/me",
    summary="Список организаций пользователя",
    description="Возвращает список всех организаций, к которым принадлежит текущий пользователь, с указанием роли.",
)
async def get_my_organizations(
    user: UserModel = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> list[dict]:
    member_repo = OrganizationMemberRepository(session)
    results = await member_repo.get_user_organizations(user.id)

    return [
        {
            "organization_id": str(member.organization_id),
            "organization_name": org.name,
            "role": member.role,
        }
        for member, org in results
    ]
