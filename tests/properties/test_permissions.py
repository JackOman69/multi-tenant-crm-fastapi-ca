from hypothesis import given
from hypothesis import strategies as st

from src.domain.value_objects.deal_stage import DealStage
from src.domain.value_objects.role import Role
from src.services.permission import PermissionService


@given(st.sampled_from([Role.OWNER, Role.ADMIN]), st.uuids(), st.uuids())
def test_owner_and_admin_full_access(role: Role, user_id, resource_owner_id):
    assert PermissionService.check_resource_permission(user_id, resource_owner_id, role)


@given(st.uuids(), st.uuids())
def test_member_resource_ownership(user_id, other_user_id):
    result = PermissionService.check_resource_permission(user_id, other_user_id, Role.MEMBER)
    assert result == (user_id == other_user_id)


@given(st.uuids())
def test_member_owns_their_resources(user_id):
    assert PermissionService.check_resource_permission(user_id, user_id, Role.MEMBER)


@given(
    st.sampled_from([Role.MEMBER, Role.MANAGER]),
    st.sampled_from(list(DealStage)),
    st.sampled_from(list(DealStage)),
)
def test_member_stage_rollback_restriction(role: Role, current_stage, new_stage):
    stage_order = {
        DealStage.QUALIFICATION: 0,
        DealStage.PROPOSAL: 1,
        DealStage.NEGOTIATION: 2,
        DealStage.CLOSED: 3,
    }

    can_rollback = PermissionService.can_rollback_stage(role, current_stage, new_stage)

    if stage_order[new_stage] < stage_order[current_stage]:
        assert not can_rollback
    else:
        assert can_rollback


@given(
    st.sampled_from([Role.OWNER, Role.ADMIN]),
    st.sampled_from(list(DealStage)),
    st.sampled_from(list(DealStage)),
)
def test_admin_owner_stage_rollback_permission(role: Role, current_stage, new_stage):
    assert PermissionService.can_rollback_stage(role, current_stage, new_stage)
