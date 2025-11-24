import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_analytics_summary_with_different_statuses(client: AsyncClient):
    register_data = {
        "email": "analytics_user@example.com",
        "password": "password123",
        "name": "Analytics User",
        "organization_name": "Analytics Org",
    }
    register_response = await client.post("/api/v1/auth/register", json=register_data)
    assert register_response.status_code == 201
    org_id = register_response.json()["organization_id"]

    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": "analytics_user@example.com", "password": "password123"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}", "X-Organization-Id": org_id}

    contact_response = await client.post(
        "/api/v1/contacts", json={"name": "Test Contact"}, headers=headers
    )
    assert contact_response.status_code == 201
    contact_id = contact_response.json()["id"]

    deal1 = await client.post(
        "/api/v1/deals",
        json={"contact_id": contact_id, "title": "Deal 1", "amount": "1000.00"},
        headers=headers,
    )
    assert deal1.status_code == 201

    deal2 = await client.post(
        "/api/v1/deals",
        json={"contact_id": contact_id, "title": "Deal 2", "amount": "2000.00"},
        headers=headers,
    )
    assert deal2.status_code == 201
    deal2_id = deal2.json()["id"]

    deal3 = await client.post(
        "/api/v1/deals",
        json={"contact_id": contact_id, "title": "Deal 3", "amount": "3000.00"},
        headers=headers,
    )
    assert deal3.status_code == 201
    deal3_id = deal3.json()["id"]

    await client.patch(
        f"/api/v1/deals/{deal2_id}", json={"status": "won"}, headers=headers
    )
    await client.patch(
        f"/api/v1/deals/{deal3_id}", json={"status": "lost"}, headers=headers
    )

    summary_response = await client.get("/api/v1/analytics/deals/summary", headers=headers)
    assert summary_response.status_code == 200

    summary = summary_response.json()
    assert summary["total_count"] == 3
    assert summary["new_count"] == 1
    assert summary["won_count"] == 1
    assert summary["lost_count"] == 1
    assert float(summary["total_amount"]) == 6000.0
    assert float(summary["won_amount"]) == 2000.0
    assert float(summary["average_won_amount"]) == 2000.0


@pytest.mark.asyncio
async def test_analytics_funnel_with_stages(client: AsyncClient):
    register_data = {
        "email": "funnel_user@example.com",
        "password": "password123",
        "name": "Funnel User",
        "organization_name": "Funnel Org",
    }
    register_response = await client.post("/api/v1/auth/register", json=register_data)
    assert register_response.status_code == 201
    org_id = register_response.json()["organization_id"]

    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": "funnel_user@example.com", "password": "password123"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}", "X-Organization-Id": org_id}

    contact_response = await client.post(
        "/api/v1/contacts", json={"name": "Funnel Contact"}, headers=headers
    )
    assert contact_response.status_code == 201
    contact_id = contact_response.json()["id"]

    deal1 = await client.post(
        "/api/v1/deals",
        json={"contact_id": contact_id, "title": "Deal Q", "amount": "1000.00"},
        headers=headers,
    )
    assert deal1.status_code == 201

    deal2 = await client.post(
        "/api/v1/deals",
        json={"contact_id": contact_id, "title": "Deal P", "amount": "2000.00"},
        headers=headers,
    )
    assert deal2.status_code == 201
    deal2_id = deal2.json()["id"]

    deal3 = await client.post(
        "/api/v1/deals",
        json={"contact_id": contact_id, "title": "Deal N", "amount": "3000.00"},
        headers=headers,
    )
    assert deal3.status_code == 201
    deal3_id = deal3.json()["id"]

    await client.patch(
        f"/api/v1/deals/{deal2_id}", json={"stage": "proposal"}, headers=headers
    )
    await client.patch(
        f"/api/v1/deals/{deal3_id}", json={"stage": "negotiation"}, headers=headers
    )

    funnel_response = await client.get("/api/v1/analytics/deals/funnel", headers=headers)
    assert funnel_response.status_code == 200

    funnel = funnel_response.json()
    assert "stages" in funnel
    assert len(funnel["stages"]) > 0

    stages_dict = {stage["stage"]: stage["count"] for stage in funnel["stages"]}
    assert stages_dict.get("qualification", 0) == 1
    assert stages_dict.get("proposal", 0) == 1
    assert stages_dict.get("negotiation", 0) == 1


@pytest.mark.asyncio
async def test_analytics_empty_organization(client: AsyncClient):
    register_data = {
        "email": "empty_user@example.com",
        "password": "password123",
        "name": "Empty User",
        "organization_name": "Empty Org",
    }
    register_response = await client.post("/api/v1/auth/register", json=register_data)
    assert register_response.status_code == 201
    org_id = register_response.json()["organization_id"]

    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": "empty_user@example.com", "password": "password123"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}", "X-Organization-Id": org_id}

    summary_response = await client.get("/api/v1/analytics/deals/summary", headers=headers)
    assert summary_response.status_code == 200

    summary = summary_response.json()
    assert summary["total_count"] == 0
    assert summary["new_count"] == 0
    assert summary["won_count"] == 0
    assert summary["lost_count"] == 0
    assert float(summary["total_amount"]) == 0.0
    assert float(summary["won_amount"]) == 0.0
    assert float(summary["average_won_amount"]) == 0.0

    funnel_response = await client.get("/api/v1/analytics/deals/funnel", headers=headers)
    assert funnel_response.status_code == 200
    funnel = funnel_response.json()
    assert "stages" in funnel
