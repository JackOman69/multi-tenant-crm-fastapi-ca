from enum import Enum


class ActivityType(str, Enum):
    """Type of activity in the deal timeline."""

    COMMENT = "comment"
    STATUS_CHANGED = "status_changed"
    STAGE_CHANGED = "stage_changed"
    TASK_CREATED = "task_created"
    SYSTEM = "system"
