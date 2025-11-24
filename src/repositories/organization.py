from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import OrganizationModel
from src.domain.entities.organization import Organization
from src.repositories.base import BaseRepository


class OrganizationRepository(BaseRepository[OrganizationModel, Organization]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, OrganizationModel)
