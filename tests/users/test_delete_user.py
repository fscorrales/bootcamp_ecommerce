from fastapi.testclient import TestClient

from ...bootcamp_ecommerce.main import app

client = TestClient(app)


def test_delete_user_without_credentials(create_and_delete_customer):
    user_id = create_and_delete_customer
    response = client.delete(f"/api/Users/{user_id}")
    assert response.status_code == 401


def test_delete_user_invalid_id(login_as_admin):
    access_token = login_as_admin.get("access_token")
    headers = {"Authorization": f"Bearer {access_token}"}
    user_id = "12345"
    response = client.delete(
        f"/api/Users/{user_id}",
        headers = headers
    )
    assert response.status_code == 422


def test_delete_user(login_as_admin, create_and_delete_customer):
    access_token = login_as_admin.get("access_token")
    headers = {"Authorization": f"Bearer {access_token}"}
    user_id = create_and_delete_customer
    response = client.delete(
        f"/api/Users/{user_id}",
        headers = headers
    )
    assert response.status_code == 200
    assert response.json().get("deactivated_at") != None