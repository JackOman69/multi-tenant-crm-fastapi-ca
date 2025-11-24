from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class Organization:
    """Organization entity representing a tenant in the multi-tenant system."""

    id: UUID
    name: str
    created_at: datetime
