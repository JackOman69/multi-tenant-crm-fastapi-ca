from dataclasses import dataclass
from uuid import UUID

from src.domain.value_objects.role import Role


@dataclass
class OrganizationMember:
    """Organization member entity representing user membership in an organization."""

    id: UUID
    organization_id: UUID
    user_id: UUID
    role: Role
