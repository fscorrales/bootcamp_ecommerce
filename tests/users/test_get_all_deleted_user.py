from fastapi.testclient import TestClient

from ...bootcamp_ecommerce.main import app

client = TestClient(app)

def test_get_all_deleted_users_without_credentials():
    response = client.get("/api/Users/deleted")
    assert response.status_code == 401


def test_get_all_deleted_users(login_as_admin):
    access_token = login_as_admin.get("access_token")
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.get(
        "/api/Users/deleted",
        headers = headers
    )
    assert response.status_code == 200