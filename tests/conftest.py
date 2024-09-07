# https://fastapi.tiangolo.com/tutorial/testing/
import pytest
from bson import ObjectId
from fastapi import Response

from ..bootcamp_ecommerce.api.models import CreationUser, LoginUser
from ..bootcamp_ecommerce.api.services import UsersServiceDependency, AuthService, AuthServiceDependency


@pytest.fixture
def dict_test_user() -> dict:
    return {
        "username": "Test",
        "email": "test@test.com",
        "role": "customer",
        "password": "12345"
    }


@pytest.fixture
def create_and_delete_admin(dict_test_user):
    user = CreationUser(**dict_test_user)
    user_id = UsersServiceDependency().create_one(
        user = user,
        hash_password = AuthServiceDependency().get_password_hash(user.password),
        make_it_admin = True
    )
    yield user_id
    UsersServiceDependency().delete_one_forever(
            id = ObjectId(user_id)
    )

@pytest.fixture
def login_as_admin(create_and_delete_admin, dict_test_user):
    user = LoginUser(**dict_test_user)
    access_token = AuthService().login_and_set_access_token(
        db_user = UsersServiceDependency().get_one(username=user.username, with_password=True),
        user=user,
        response=Response()
    )
    return access_token


@pytest.fixture
def create_and_delete_customer(dict_test_user):
    dict_test_user["role"] = "customer"
    user = CreationUser(**dict_test_user)
    user_id = UsersServiceDependency().create_one(
        user = user,
        hash_password = user.password
    )
    yield user_id
    UsersServiceDependency().delete_one_forever(
            id = ObjectId(user_id)
    )


@pytest.fixture
def create_and_delete_seller(dict_test_user):
    dict_test_user["role"] = "seller"
    user = CreationUser(**dict_test_user)
    user_id = UsersServiceDependency().create_one(
        user = user,
        hash_password = user.password
    )
    yield user_id
    UsersServiceDependency().delete_one_forever(
            id = ObjectId(user_id)
    )