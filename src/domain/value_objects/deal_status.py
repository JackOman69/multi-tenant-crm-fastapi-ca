from enum import Enum


class DealStatus(str, Enum):
    """Status of a deal in the sales pipeline."""

    NEW = "new"
    IN_PROGRESS = "in_progress"
    WON = "won"
    LOST = "lost"
