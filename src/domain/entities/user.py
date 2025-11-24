from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class User:
    """User entity representing a registered user in the system."""

    id: UUID
    email: str
    hashed_password: str
    name: str
    created_at: datetime
