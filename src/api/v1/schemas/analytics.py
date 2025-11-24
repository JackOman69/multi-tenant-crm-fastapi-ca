from decimal import Decimal

from pydantic import BaseModel


class DealSummaryResponse(BaseModel):
    total_count: int
    new_count: int
    in_progress_count: int
    won_count: int
    lost_count: int
    total_amount: Decimal
    won_amount: Decimal
    average_won_amount: Decimal


class FunnelStageResponse(BaseModel):
    stage: str
    count: int


class FunnelResponse(BaseModel):
    stages: list[FunnelStageResponse]
