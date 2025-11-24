"""Role value object."""
from enum import Enum


class Role(str, Enum):
    """User role within an organization."""

    OWNER = "owner"
    ADMIN = "admin"
    MANAGER = "manager"
    MEMBER = "member"
