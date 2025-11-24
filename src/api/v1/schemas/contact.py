from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ContactCreate(BaseModel):
    name: str
    email: str | None = None
    phone: str | None = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Jane Smith",
                    "email": "jane@example.com",
                    "phone": "+1234567890",
                }
            ]
        }
    }


class ContactUpdate(BaseModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None


class ContactResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    owner_id: UUID
    name: str
    email: str | None
    phone: str | None
    created_at: datetime


class ContactListResponse(BaseModel):
    items: list[ContactResponse]
    total: int
    limit: int
    offset: int
