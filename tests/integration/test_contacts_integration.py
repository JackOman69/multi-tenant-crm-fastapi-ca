import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_contacts_crud(client: AsyncClient):
    register_data = {
        "email": "contacts@example.com",
        "password": "password123",
        "name": "Contacts User",
        "organization_name": "Contacts Org",
    }
    register_response = await client.post("/api/v1/auth/register", json=register_data)
    assert register_response.status_code == 201
    org_id = register_response.json()["organization_id"]

    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": "contacts@example.com", "password": "password123"},
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}", "X-Organization-Id": org_id}

    create_response = await client.post(
        "/api/v1/contacts",
        json={"name": "Test Contact", "email": "test@example.com", "phone": "+123"},
        headers=headers,
    )
    assert create_response.status_code == 201
    contact = create_response.json()
    contact_id = contact["id"]
    assert contact["name"] == "Test Contact"
    assert contact["email"] == "test@example.com"

    get_response = await client.get(f"/api/v1/contacts/{contact_id}", headers=headers)
    assert get_response.status_code == 200
    assert get_response.json()["id"] == contact_id

    update_response = await client.patch(
        f"/api/v1/contacts/{contact_id}",
        json={"name": "Updated Contact"},
        headers=headers,
    )
    assert update_response.status_code == 200
    assert update_response.json()["name"] == "Updated Contact"

    delete_response = await client.delete(
        f"/api/v1/contacts/{contact_id}", headers=headers
    )
    assert delete_response.status_code == 204


@pytest.mark.asyncio
async def test_contacts_pagination_and_search(client: AsyncClient):
    register_data = {
        "email": "pagination@example.com",
        "password": "password123",
        "name": "Pagination User",
        "organization_name": "Pagination Org",
    }
    register_response = await client.post("/api/v1/auth/register", json=register_data)
    org_id = register_response.json()["organization_id"]

    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": "pagination@example.com", "password": "password123"},
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}", "X-Organization-Id": org_id}

    for i in range(5):
        await client.post(
            "/api/v1/contacts",
            json={"name": f"Contact {i}", "email": f"contact{i}@example.com"},
            headers=headers,
        )

    list_response = await client.get(
        "/api/v1/contacts?limit=3&offset=0", headers=headers
    )
    assert list_response.status_code == 200
    data = list_response.json()
    assert data["total"] == 5
    assert len(data["items"]) == 3

    search_response = await client.get(
        "/api/v1/contacts?search=Contact 2", headers=headers
    )
    assert search_response.status_code == 200
    search_data = search_response.json()
    assert len(search_data["items"]) >= 1
    assert "Contact 2" in search_data["items"][0]["name"]
