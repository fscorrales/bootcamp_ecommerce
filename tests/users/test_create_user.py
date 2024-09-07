
import pytest

from bson import ObjectId
from fastapi.testclient import TestClient

from ...bootcamp_ecommerce.main import app
from ...bootcamp_ecommerce.api.services import UsersServiceDependency

client = TestClient(app)


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