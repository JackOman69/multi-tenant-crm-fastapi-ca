import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_activity_timeline(client: AsyncClient):
    register_data = {
        "email": "activity@example.com",
        "password": "password123",
        "name": "Activity User",
        "organization_name": "Activity Org",
    }
    register_response = await client.post("/api/v1/auth/register", json=register_data)
    org_id = register_response.json()["organization_id"]

    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": "activity@example.com", "password": "password123"},
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}", "X-Organization-Id": org_id}

    contact_response = await client.post(
        "/api/v1/contacts", json={"name": "Activity Contact"}, headers=headers
    )
    contact_id = contact_response.json()["id"]

    deal_response = await client.post(
        "/api/v1/deals",
        json={
            "contact_id": contact_id,
            "title": "Activity Deal",
            "amount": "2000.00",
        },
        headers=headers,
    )
    deal_id = deal_response.json()["id"]

    comment_response = await client.post(
        f"/api/v1/deals/{deal_id}/activities",
        json={"content": "First comment"},
        headers=headers,
    )
    assert comment_response.status_code == 201
    comment = comment_response.json()
    assert comment["type"] == "comment"
    assert comment["payload"]["content"] == "First comment"
    assert comment["author_id"] is not None

    await client.patch(
        f"/api/v1/deals/{deal_id}", json={"stage": "negotiation"}, headers=headers
    )

    await client.patch(
        f"/api/v1/deals/{deal_id}", json={"status": "won"}, headers=headers
    )

    activities_response = await client.get(
        f"/api/v1/deals/{deal_id}/activities", headers=headers
    )
    assert activities_response.status_code == 200
    activities = activities_response.json()["items"]
    assert len(activities) >= 3

    comment_activity = next((a for a in activities if a["type"] == "comment"), None)
    assert comment_activity is not None
    assert comment_activity["payload"]["content"] == "First comment"

    stage_activity = next(
        (a for a in activities if a["type"] == "stage_changed"), None
    )
    assert stage_activity is not None
    assert stage_activity["author_id"] is None

    status_activity = next(
        (a for a in activities if a["type"] == "status_changed"), None
    )
    assert status_activity is not None
    assert status_activity["author_id"] is None
