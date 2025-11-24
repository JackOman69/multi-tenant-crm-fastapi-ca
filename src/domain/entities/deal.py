from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from src.domain.value_objects.deal_stage import DealStage
from src.domain.value_objects.deal_status import DealStatus


@dataclass
class Deal:
    """Deal entity representing a sales opportunity."""

    id: UUID
    organization_id: UUID
    contact_id: UUID
    owner_id: UUID
    title: str
    amount: Decimal
    currency: str
    status: DealStatus
    stage: DealStage
    created_at: datetime
    updated_at: datetime
