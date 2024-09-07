from fastapi.testclient import TestClient

from ...bootcamp_ecommerce.main import app

client = TestClient(app)

def test_authenticated_user_without_credentials():
    response = client.get(
        "/auth/authenticated_user/"
    )
    assert response.status_code == 401


def test_authenticated_user(login_as_admin):
    access_token = login_as_admin.get("access_token")
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.get(
        "/auth/authenticated_user/",
        headers = headers
    )
    assert response.status_code == 200
    print(response.json())