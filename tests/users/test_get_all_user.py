import jsonschema
from fastapi.testclient import TestClient

from ...bootcamp_ecommerce.main import app

client = TestClient(app)

def test_get_all_users_without_credentials():
    response = client.get("/api/Users/include_deleted")
    assert response.status_code == 401


def test_get_all_users(login_as_admin, active_users_schema):
    access_token = login_as_admin.get("access_token")
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.get(
        "/api/Users/include_deleted",
        headers = headers
    )
    assert response.status_code == 200
    jsonschema.validate(
        instance=response.json(), schema=active_users_schema
    )