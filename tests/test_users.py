# https://fastapi.tiangolo.com/tutorial/testing/
import jsonschema
import pytest
from fastapi.testclient import TestClient

from ..bootcamp_ecommerce.main import app

client = TestClient(app)

@pytest.fixture


def test_create_user():
    response = client.post(
        "/api/Users/", 
        json={
            "username": "Test",
            "email": "test@test.com",
            "role": "customer",
            "password": "12345"
        }
    )
    assert response.status_code == 200
    print(response.json())

# async def override_user_dependency():
#     return {
#         "username": "test",
#         "email": "test",
#         "password": "test",
#         "role": "admin",
#     }


@pytest.mark.skip
def test_get_all_active_users():
    active_users_schema = {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "username": {"type": "string"},
                "email": {"type": ["string", "null"]},
                "image": {"type": ["string", "null"]},
                "role": {"type": "string"},
                "deactivated_at": {"type": ["string", "null"]}
            },
            "required": ["id", "username", "role"]
        }
    }

    response = client.get("/api/Users/")
    assert response.status_code == 200
    jsonschema.validate(
        instance=response.json(), schema=active_users_schema
    )

