import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from src.db.models import OrganizationMemberModel, OrganizationModel, Role, UserModel
from src.repositories.organization_member import OrganizationMemberRepository


@pytest.mark.asyncio
@settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=5)
@given(org_count=st.integers(min_value=1, max_value=5))
async def test_user_organizations_list_completeness(db_session, org_count):
    import uuid

    user = UserModel(
        email=f"user_{uuid.uuid4().hex[:8]}@example.com",
        hashed_password="hashed",
        name="Test User",
    )
    db_session.add(user)
    await db_session.flush()

    created_orgs = []
    for i in range(org_count):
        org = OrganizationModel(name=f"Org {i}")
        db_session.add(org)
        await db_session.flush()

        member = OrganizationMemberModel(
            user_id=user.id, organization_id=org.id, role=Role.MEMBER
        )
        db_session.add(member)
        created_orgs.append((org.id, org.name, Role.MEMBER))

    await db_session.commit()

    repo = OrganizationMemberRepository(db_session)
    user_orgs = await repo.get_user_organizations(user.id)

    assert len(user_orgs) == org_count

    for member, org in user_orgs:
        assert member.organization_id == org.id
        assert member.user_id == user.id
        assert org.name is not None
        assert member.role in [Role.OWNER, Role.ADMIN, Role.MEMBER]

    retrieved_org_ids = {member.organization_id for member, org in user_orgs}
    expected_org_ids = {org_id for org_id, _, _ in created_orgs}
    assert retrieved_org_ids == expected_org_ids
