from uuid import UUID

from src.domain.value_objects.deal_stage import DealStage
from src.domain.value_objects.role import Role


class PermissionService:
    @staticmethod
    def check_organization_access(user_role: Role | None) -> bool:
        return user_role is not None

    @staticmethod
    def check_resource_permission(
        user_id: UUID, resource_owner_id: UUID, user_role: Role
    ) -> bool:
        if user_role in (Role.OWNER, Role.ADMIN):
            return True
        return user_id == resource_owner_id

    @staticmethod
    def can_rollback_stage(user_role: Role, current_stage: DealStage, new_stage: DealStage) -> bool:
        stage_order = {
            DealStage.QUALIFICATION: 0,
            DealStage.PROPOSAL: 1,
            DealStage.NEGOTIATION: 2,
            DealStage.CLOSED: 3,
        }

        if stage_order[new_stage] >= stage_order[current_stage]:
            return True

        if user_role in (Role.OWNER, Role.ADMIN):
            return True

        return False
