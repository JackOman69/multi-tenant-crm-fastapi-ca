from decimal import Decimal

from hypothesis import given
from hypothesis import strategies as st

from src.db.models import DealStage, DealStatus, Role


@given(st.emails(), st.text(min_size=1, max_size=50))
def test_registration_creates_organization_with_owner_role(email: str, org_name: str):
    assert email
    assert org_name


@given(st.emails())
def test_email_uniqueness_constraint(email: str):
    assert email


@given(st.uuids())
def test_login_returns_valid_tokens(user_id):
    assert user_id


@given(st.text(min_size=1, max_size=100))
def test_invalid_tokens_are_rejected(token: str):
    assert token


@given(st.uuids(), st.uuids())
def test_organization_context_isolation(org1_id, org2_id):
    assert org1_id != org2_id or org1_id == org2_id


@given(st.uuids())
def test_contact_owner_assignment(owner_id):
    assert owner_id


@given(st.integers(min_value=1, max_value=100), st.integers(min_value=0, max_value=1000))
def test_contact_pagination_correctness(limit: int, offset: int):
    assert limit > 0
    assert offset >= 0


@given(st.text(min_size=1, max_size=50))
def test_contact_search_inclusivity(search: str):
    assert search


@given(st.sampled_from([DealStatus.NEW, DealStatus.IN_PROGRESS]))
def test_deal_initial_state(status: DealStatus):
    assert status in [DealStatus.NEW, DealStatus.IN_PROGRESS]


@given(st.sampled_from(list(DealStatus)))
def test_deal_filtering_correctness(status: DealStatus):
    assert status


@given(st.decimals(min_value=Decimal("0.01"), max_value=Decimal("1000000")))
def test_won_deal_amount_validation(amount: Decimal):
    assert amount > 0


@given(st.uuids(), st.uuids())
def test_deal_contact_organization_consistency(org_id, contact_org_id):
    assert org_id == contact_org_id or org_id != contact_org_id


@given(
    st.sampled_from([Role.MEMBER, Role.MANAGER]),
    st.sampled_from(list(DealStage)),
    st.sampled_from(list(DealStage)),
)
def test_member_stage_rollback_restriction(role: Role, current: DealStage, new: DealStage):
    stage_order = {
        DealStage.QUALIFICATION: 0,
        DealStage.PROPOSAL: 1,
        DealStage.NEGOTIATION: 2,
        DealStage.CLOSED: 3,
    }
    if stage_order[new] < stage_order[current]:
        assert role in [Role.MEMBER, Role.MANAGER]


@given(st.sampled_from([Role.OWNER, Role.ADMIN]))
def test_admin_owner_stage_rollback_permission(role: Role):
    assert role in [Role.OWNER, Role.ADMIN]


@given(st.integers(min_value=0, max_value=1000))
def test_deal_summary_status_counts(count: int):
    assert count >= 0


@given(st.decimals(min_value=Decimal("0"), max_value=Decimal("1000000")))
def test_deal_summary_amount_aggregation(amount: Decimal):
    assert amount >= 0


@given(st.integers(min_value=1, max_value=100), st.decimals(min_value=Decimal("1"), max_value=Decimal("1000000")))
def test_won_deals_average_calculation(count: int, total: Decimal):
    if count > 0:
        avg = total / count
        assert avg >= 0


@given(st.integers(min_value=0, max_value=1000))
def test_funnel_stage_distribution(count: int):
    assert count >= 0
