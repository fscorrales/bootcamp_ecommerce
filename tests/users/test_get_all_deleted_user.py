from fastapi.testclient import TestClient

from ...bootcamp_ecommerce.main import app

client = TestClient(app)

def test_get_all_deleted_users_without_credentials():
    response = client.get("/api/Users/deleted")
    assert response.status_code == 401


def test_get_all_deleted_users(login_as_admin):
    print(login_as_admin)
    response = client.get("/api/Users/deleted")
    assert response.status_code == 200