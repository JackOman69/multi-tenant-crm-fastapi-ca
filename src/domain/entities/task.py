from dataclasses import dataclass
from datetime import date, datetime
from uuid import UUID


@dataclass
class Task:
    """Task entity representing a todo item for a deal."""

    id: UUID
    deal_id: UUID
    title: str
    description: str | None
    due_date: date
    is_done: bool
    created_at: datetime
