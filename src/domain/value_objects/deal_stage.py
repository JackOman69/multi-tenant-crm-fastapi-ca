from enum import Enum


class DealStage(str, Enum):
    """Stage of a deal in the sales funnel."""

    QUALIFICATION = "qualification"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    CLOSED = "closed"
