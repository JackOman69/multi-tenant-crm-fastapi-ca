"""Activity entity."""
from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID

from src.domain.value_objects.activity_type import ActivityType


@dataclass
class Activity:
    """Activity entity representing an event in the deal timeline."""

    id: UUID
    deal_id: UUID
    author_id: UUID | None
    type: ActivityType
    payload: dict[str, Any]
    created_at: datetime
