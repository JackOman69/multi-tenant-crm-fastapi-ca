from datetime import date, timedelta

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_tasks_crud(client: AsyncClient):
    register_data = {
        "email": "tasks@example.com",
        "password": "password123",
        "name": "Tasks User",
        "organization_name": "Tasks Org",
    }
    register_response = await client.post("/api/v1/auth/register", json=register_data)
    org_id = register_response.json()["organization_id"]

    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": "tasks@example.com", "password": "password123"},
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}", "X-Organization-Id": org_id}

    contact_response = await client.post(
        "/api/v1/contacts",
        json={"name": "Task Contact"},
        headers=headers,
    )
    contact_id = contact_response.json()["id"]

    deal_response = await client.post(
        "/api/v1/deals",
        json={
            "contact_id": contact_id,
            "title": "Task Deal",
            "amount": "1000.00",
        },
        headers=headers,
    )
    deal_id = deal_response.json()["id"]

    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    create_response = await client.post(
        "/api/v1/tasks",
        json={
            "title": "Test Task",
            "description": "Task description",
            "due_date": tomorrow,
        },
        params={"deal_id": deal_id},
        headers=headers,
    )
    assert create_response.status_code == 201
    task = create_response.json()
    assert task["title"] == "Test Task"
    assert task["is_done"] is False


@pytest.mark.asyncio
async def test_tasks_filtering(client: AsyncClient):
    register_data = {
        "email": "taskfilter@example.com",
        "password": "password123",
        "name": "Filter User",
        "organization_name": "Filter Org",
    }
    register_response = await client.post("/api/v1/auth/register", json=register_data)
    org_id = register_response.json()["organization_id"]

    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": "taskfilter@example.com", "password": "password123"},
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}", "X-Organization-Id": org_id}

    contact_response = await client.post(
        "/api/v1/contacts", json={"name": "Filter Contact"}, headers=headers
    )
    contact_id = contact_response.json()["id"]

    deal_response = await client.post(
        "/api/v1/deals",
        json={"contact_id": contact_id, "title": "Filter Deal", "amount": "1000.00"},
        headers=headers,
    )
    deal_id = deal_response.json()["id"]

    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    for i in range(3):
        await client.post(
            "/api/v1/tasks",
            json={"title": f"Task {i}", "due_date": tomorrow},
            params={"deal_id": deal_id},
            headers=headers,
        )

    list_response = await client.get(
        f"/api/v1/tasks?deal_id={deal_id}", headers=headers
    )
    assert list_response.status_code == 200
    tasks = list_response.json()["items"]
    assert len(tasks) == 3

    task_id = tasks[0]["id"]
    await client.patch(
        f"/api/v1/tasks/{task_id}", json={"is_done": True}, headers=headers
    )

    open_response = await client.get(
        f"/api/v1/tasks?deal_id={deal_id}&only_open=true", headers=headers
    )
    assert open_response.status_code == 200
    open_tasks = open_response.json()["items"]
    assert len(open_tasks) == 2
