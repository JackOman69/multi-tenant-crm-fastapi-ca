from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import ContactModel, DealModel, DealStatus
from src.domain.entities.contact import Contact
from src.repositories.base import BaseRepository


class ContactRepository(BaseRepository[ContactModel, Contact]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, ContactModel)

    async def list_by_organization(
        self,
        organization_id: UUID,
        limit: int = 50,
        offset: int = 0,
        search: str | None = None,
    ) -> tuple[list[ContactModel], int]:
        query = select(ContactModel).where(ContactModel.organization_id == organization_id)

        if search:
            search_pattern = f"%{search}%"
            query = query.where(
                (ContactModel.name.ilike(search_pattern))
                | (ContactModel.email.ilike(search_pattern))
                | (ContactModel.phone.ilike(search_pattern))
            )

        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.session.execute(count_query)
        total = total_result.scalar_one()

        query = query.limit(limit).offset(offset)
        result = await self.session.execute(query)
        contacts = list(result.scalars().all())

        return contacts, total

    async def has_active_deals(self, contact_id: UUID) -> bool:
        result = await self.session.execute(
            select(func.count())
            .select_from(DealModel)
            .where(
                DealModel.contact_id == contact_id,
                DealModel.status.in_([DealStatus.NEW, DealStatus.IN_PROGRESS]),
            )
        )
        count = result.scalar_one()
        return count > 0
