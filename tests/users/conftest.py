# https://fastapi.tiangolo.com/tutorial/testing/
import jsonschema
import pytest
from bson import ObjectId

from ...bootcamp_ecommerce.api.models import CreationUser
from ...bootcamp_ecommerce.api.services import UsersServiceDependency, SecurityDependency


@pytest.fixture
def dict_test_user() -> dict:
    return {
        "username": "Test",
        "email": "test@test.com",
        "role": "customer",
        "password": "12345"
    }

@pytest.fixture
def active_users_schema():
    return {
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

# @pytest.fixture
# async def override_security_dependency(dict_test_user):
#     class SecurityServiceOverride:
#         def __init__(self):
#             self.auth_user_id = ObjectId()
#             self.auth_user_name = dict_test_user.get("username")
#             self.auth_user_email = dict_test_user.get("email")
#             self.auth_user_role = 'admin'
#     return SecurityServiceOverride()

# @pytest.fixture
# def add_and_remove_security_dependency(override_security_dependency):
#     app.dependency_overrides[SecurityDependency] = override_security_dependency
#     yield
#     app.dependency_overrides = {}