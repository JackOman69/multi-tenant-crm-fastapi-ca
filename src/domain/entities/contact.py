from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class Contact:
    """Contact entity representing a potential or existing customer."""

    id: UUID
    organization_id: UUID
    owner_id: UUID
    name: str
    email: str | None
    phone: str | None
    created_at: datetime
