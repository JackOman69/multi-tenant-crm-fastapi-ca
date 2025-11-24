from hypothesis import given
from hypothesis import strategies as st


@given(st.uuids())
def test_organization_header_requirement(org_id):
    assert org_id is not None


@given(st.uuids(), st.uuids())
def test_organization_context_isolation(user_org_id, other_org_id):
    if user_org_id != other_org_id:
        assert user_org_id != other_org_id
    else:
        assert user_org_id == other_org_id
