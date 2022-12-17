from fastapi.testclient import TestClient
import json


def test_login(client: TestClient):

    data = {"username":"cat@gmail.com", "password":"1234"}
    response = client.post("/auth/login", data=data)
    
    assert response.status_code == 200
    assert response.json()["access_token"] is not None
    assert response.json()["refresh_token"] is not None


def test_invalid_email_login(client: TestClient):
    
    data = {"username":"cat228@gmail.com", "password":"1234"}
    response = client.post("/auth/login", data=data)
    
    assert response.status_code == 404
    assert response.json()["detail"] == f'No user with email {data["username"]}'


def test_invalid_password_login(client: TestClient):
    
    data = {"username":"cat@gmail.com", "password":"12345678"}
    response = client.post("/auth/login", data=data)
    
    assert response.status_code == 404
    assert response.json()["detail"] == 'Incorrect password'