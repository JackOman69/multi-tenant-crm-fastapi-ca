from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import OrganizationMemberModel, OrganizationModel
from src.domain.entities.organization_member import OrganizationMember
from src.repositories.base import BaseRepository


class OrganizationMemberRepository(BaseRepository[OrganizationMemberModel, OrganizationMember]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, OrganizationMemberModel)

    async def get_user_organizations(self, user_id: UUID) -> list[tuple[OrganizationMemberModel, OrganizationModel]]:
        result = await self.session.execute(
            select(OrganizationMemberModel, OrganizationModel)
            .join(OrganizationModel, OrganizationMemberModel.organization_id == OrganizationModel.id)
            .where(OrganizationMemberModel.user_id == user_id)
        )
        return list(result.all())
