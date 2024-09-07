# https://fastapi.tiangolo.com/tutorial/testing/
import jsonschema
import pytest
from bson import ObjectId
from fastapi.testclient import TestClient

from ..bootcamp_ecommerce.api.models import CreationUser
from ..bootcamp_ecommerce.api.services import UsersServiceDependency, SecurityDependency
from ..bootcamp_ecommerce.main import app

client = TestClient(app)


@pytest.fixture
def dict_test_user() -> dict:
    return {
        "username": "Test",
        "email": "test@test.com",
        "role": "customer",
        "password": "12345"
    }


@pytest.fixture
def create_and_delete_user(dict_test_user):
    user = CreationUser(**dict_test_user)
    user_id = UsersServiceDependency().create_one(
        user = user,
        hash_password = user.password
    )
    yield user_id
    UsersServiceDependency().delete_one_forever(
            id = ObjectId(user_id)
    )


def test_create_user_without_body():
    response = client.post(
        "/api/Users/", 
        json={}
    )
    print(response.json())
    assert response.status_code == 422


def test_create_user(dict_test_user):
    response = client.post(
        "/api/Users/", 
        json=dict_test_user
    )
    print(response.json())
    assert response.status_code == 200
    if user_id:=response.json().get("user_id"):
        UsersServiceDependency().delete_one_forever(
            id = ObjectId(user_id)
        )


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
    print(response.json())
    assert response.status_code == 200
    jsonschema.validate(
        instance=response.json(), schema=active_users_schema
    )


def test_get_all_deleted_users_without_credentials():
    response = client.get("/api/Users/deleted")
    print(response.json())
    assert response.status_code == 401


@pytest.fixture
async def override_security_dependency(dict_test_user):
    class SecurityServiceOverride:
        def __init__(self):
            self.auth_user_id = ObjectId()
            self.auth_user_name = dict_test_user.get("username")
            self.auth_user_email = dict_test_user.get("email")
            self.auth_user_role = 'admin'
    return SecurityServiceOverride()

@pytest.fixture
def add_and_remove_security_dependency(override_security_dependency):
    app.dependency_overrides[SecurityDependency] = override_security_dependency
    yield
    app.dependency_overrides = {}


def test_get_all_users_deleted_users(add_and_remove_security_dependency):
    response = client.get("/api/Users/deleted")
    print(response.json())
    assert response.status_code == 200


def test_get_one_user(create_and_delete_user, dict_test_user):
    user_id = create_and_delete_user
    response = client.get(f"/api/Users/{user_id}")
    print(response.json())
    assert response.status_code == 200
    created_user = dict_test_user
    created_user["id"] = str(user_id)
    created_user["deactivated_at"] = None
    created_user["image"] = None
    created_user.pop('password')
    assert response.json() == created_user


def test_get_one_user_invalid_id(create_and_delete_user):
    user_id = "12345"
    response = client.get(f"/api/Users/{user_id}")
    print(response.json())
    assert response.status_code == 422


def test_get_one_user_with_nonexitent_id(create_and_delete_user):
    user_id = ObjectId()
    response = client.get(f"/api/Users/{user_id}")
    print(response.json())
    assert response.status_code == 404


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