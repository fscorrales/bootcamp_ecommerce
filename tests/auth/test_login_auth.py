from fastapi.testclient import TestClient

from ...bootcamp_ecommerce.main import app

client = TestClient(app)

def test_login_auth_without_body():
    response = client.post(
        "/auth/login/",
        json={}
    )
    assert response.status_code == 422

def test_login_auth(create_and_delete_admin, dict_test_user):
    response = client.post(
        "/auth/login/",
        json = dict_test_user
    )
    assert response.status_code == 200