import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_full_auth_flow(client: AsyncClient):
    register_data = {
        "email": "authflow@example.com",
        "password": "password123",
        "name": "Auth User",
        "organization_name": "Auth Org",
    }
    register_response = await client.post("/api/v1/auth/register", json=register_data)
    assert register_response.status_code == 201
    register_json = register_response.json()
    assert "id" in register_json
    assert "organization_id" in register_json
    org_id = register_json["organization_id"]

    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": "authflow@example.com", "password": "password123"},
    )
    assert login_response.status_code == 200
    login_json = login_response.json()
    assert "access_token" in login_json
    assert "refresh_token" in login_json
    token = login_json["access_token"]

    headers = {"Authorization": f"Bearer {token}", "X-Organization-Id": org_id}
    orgs_response = await client.get("/api/v1/organizations/me", headers=headers)
    assert orgs_response.status_code == 200
    orgs = orgs_response.json()
    assert len(orgs) == 1
    assert orgs[0]["organization_id"] == org_id
    assert orgs[0]["role"] == "owner"
