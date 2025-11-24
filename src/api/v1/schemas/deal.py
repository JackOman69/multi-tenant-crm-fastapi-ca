from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from src.db.models import DealStage, DealStatus


class DealCreate(BaseModel):
    contact_id: UUID
    title: str
    amount: Decimal
    currency: str = "USD"

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "contact_id": "123e4567-e89b-12d3-a456-426614174000",
                    "title": "Big Deal",
                    "amount": "10000.00",
                    "currency": "USD",
                }
            ]
        }
    }


class DealUpdate(BaseModel):
    title: str | None = None
    amount: Decimal | None = None
    status: DealStatus | None = None
    stage: DealStage | None = None


class DealResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

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


class DealListResponse(BaseModel):
    items: list[DealResponse]
    total: int
    limit: int
    offset: int
