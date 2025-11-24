from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import ContactModel
from src.domain.exceptions import AuthorizationError, ConflictError, NotFoundError
from src.repositories.contact import ContactRepository
from src.services.permission import PermissionService


class ContactService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.contact_repo = ContactRepository(session)

    async def create_contact(
        self,
        organization_id: UUID,
        owner_id: UUID,
        name: str,
        email: str | None,
        phone: str | None,
    ) -> ContactModel:
        contact = ContactModel(
            id=uuid4(),
            organization_id=organization_id,
            owner_id=owner_id,
            name=name,
            email=email,
            phone=phone,
        )
        return await self.contact_repo.create(contact)

    async def list_contacts(
        self,
        organization_id: UUID,
        limit: int = 50,
        offset: int = 0,
        search: str | None = None,
    ) -> tuple[list[ContactModel], int]:
        return await self.contact_repo.list_by_organization(
            organization_id, limit, offset, search
        )

    async def get_contact(
        self,
        contact_id: UUID,
        organization_id: UUID,
    ) -> ContactModel:
        contact = await self.contact_repo.get_by_id(contact_id)
        if not contact:
            raise NotFoundError("Contact not found")
        if contact.organization_id != organization_id:
            raise NotFoundError("Contact not found")
        return contact

    async def update_contact(
        self,
        contact_id: UUID,
        user_id: UUID,
        user_role,
        name: str | None = None,
        email: str | None = None,
        phone: str | None = None,
    ) -> ContactModel:
        contact = await self.contact_repo.get_by_id(contact_id)
        if not contact:
            raise NotFoundError("Contact not found")

        if not PermissionService.check_resource_permission(user_id, contact.owner_id, user_role):
            raise AuthorizationError("Access denied")

        if name is not None:
            contact.name = name
        if email is not None:
            contact.email = email
        if phone is not None:
            contact.phone = phone

        return await self.contact_repo.update(contact)

    async def delete_contact(
        self, contact_id: UUID, user_id: UUID, user_role
    ) -> None:
        contact = await self.contact_repo.get_by_id(contact_id)
        if not contact:
            raise NotFoundError("Contact not found")

        if not PermissionService.check_resource_permission(user_id, contact.owner_id, user_role):
            raise AuthorizationError("Access denied")

        if await self.contact_repo.has_active_deals(contact_id):
            raise ConflictError("Cannot delete contact with active deals")

        await self.contact_repo.delete(contact)
