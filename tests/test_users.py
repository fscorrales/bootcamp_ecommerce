# https://fastapi.tiangolo.com/tutorial/testing/
import jsonschema
import pytest
from bson import ObjectId
from fastapi.testclient import TestClient

from ..bootcamp_ecommerce.api.services import UsersServiceDependency
from ..bootcamp_ecommerce.main import app

client = TestClient(app)


def test_create_user_without_body():
    response = client.post(
        "/api/Users/", 
        json={}
    )
    assert response.status_code == 422
    print(response.json())


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
    if user_id:=response.json().get("user_id"):
        UsersServiceDependency().delete_one_forever(
            id = ObjectId(user_id)
        )
    print(response.json())


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


def test_get_all_deleted_users():
    pass


def test_get_all_users():
    pass


def test_get_one_user():
    pass


def test_update_user():
    pass


def test_delete_user():
    pass

# async def override_user_dependency():
#     return {
#         "username": "test",
#         "email": "test",
#         "password": "test",
#         "role": "admin",
#     }