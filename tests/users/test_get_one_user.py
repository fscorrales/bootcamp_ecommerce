from bson import ObjectId
from fastapi.testclient import TestClient

from ...bootcamp_ecommerce.main import app

client = TestClient(app)


def test_get_one_user(create_and_delete_customer, dict_test_user):
    user_id = create_and_delete_customer
    response = client.get(f"/api/users/{user_id}")
    print(response.json())
    assert response.status_code == 200
    created_user = dict_test_user
    created_user["id"] = str(user_id)
    created_user["deactivated_at"] = None
    created_user["image"] = None
    created_user.pop("password")
    assert response.json() == created_user


def test_get_one_user_invalid_id():
    user_id = "12345"
    response = client.get(f"/api/users/{user_id}")
    print(response.json())
    assert response.status_code == 422


def test_get_one_user_with_nonexitent_id():
    user_id = ObjectId()
    response = client.get(f"/api/users/{user_id}")
    print(response.json())
    assert response.status_code == 404
