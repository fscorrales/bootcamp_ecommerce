import jsonschema
from fastapi.testclient import TestClient

from ...bootcamp_ecommerce.main import app

client = TestClient(app)


def test_get_all_active_users(active_users_schema):
    response = client.get("/api/users/")
    print(response.json())
    assert response.status_code == 200
    jsonschema.validate(instance=response.json(), schema=active_users_schema)
