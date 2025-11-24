import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_deal_lifecycle(client: AsyncClient):
    register_data = {
        "email": "deals@example.com",
        "password": "password123",
        "name": "Deals User",
        "organization_name": "Deals Org",
    }
    register_response = await client.post("/api/v1/auth/register", json=register_data)
    org_id = register_response.json()["organization_id"]

    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": "deals@example.com", "password": "password123"},
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}", "X-Organization-Id": org_id}

    contact_response = await client.post(
        "/api/v1/contacts",
        json={"name": "Deal Contact", "email": "deal@example.com"},
        headers=headers,
    )
    contact_id = contact_response.json()["id"]

    create_response = await client.post(
        "/api/v1/deals",
        json={
            "contact_id": contact_id,
            "title": "Test Deal",
            "amount": "5000.00",
            "currency": "USD",
        },
        headers=headers,
    )
    assert create_response.status_code == 201
    deal = create_response.json()
    deal_id = deal["id"]
    assert deal["status"] == "new"
    assert deal["stage"] == "qualification"

    stage_response = await client.patch(
        f"/api/v1/deals/{deal_id}", json={"stage": "proposal"}, headers=headers
    )
    assert stage_response.status_code == 200
    assert stage_response.json()["stage"] == "proposal"

    status_response = await client.patch(
        f"/api/v1/deals/{deal_id}", json={"status": "won"}, headers=headers
    )
    assert status_response.status_code == 200
    assert status_response.json()["status"] == "won"

    activities_response = await client.get(
        f"/api/v1/deals/{deal_id}/activities", headers=headers
    )
    assert activities_response.status_code == 200
    activities = activities_response.json()["items"]
    assert len(activities) >= 2

    stage_activity = next(
        (a for a in activities if a["type"] == "stage_changed"), None
    )
    assert stage_activity is not None
    assert stage_activity["payload"]["new_stage"] == "proposal"

    status_activity = next(
        (a for a in activities if a["type"] == "status_changed"), None
    )
    assert status_activity is not None
    assert status_activity["payload"]["new_status"] == "won"
