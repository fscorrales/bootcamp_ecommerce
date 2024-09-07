from fastapi.testclient import TestClient

from ...bootcamp_ecommerce.main import app

client = TestClient(app)

def test_get_all_deleted_users_without_credentials():
    response = client.get("/api/Users/deleted")
    print(response.json())
    assert response.status_code == 401


# def test_get_all_users_deleted_users(add_and_remove_security_dependency):
#     response = client.get("/api/Users/deleted")
#     print(response.json())
#     assert response.status_code == 200