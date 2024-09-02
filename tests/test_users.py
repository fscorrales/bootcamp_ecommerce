# https://fastapi.tiangolo.com/tutorial/testing/
import jsonschema
from fastapi.testclient import TestClient

from ..bootcamp_ecommerce.main import app

client = TestClient(app)

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

