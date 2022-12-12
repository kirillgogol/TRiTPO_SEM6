from fastapi.testclient import TestClient
import json


def test_create_user(client: TestClient):
    data = {"username":"cat", "email":"cat@gmail.com", "password":"1234"}
    response = client.post("/user/", data=json.dumps(data))
    print(response.status_code)
    assert response.status_code == 201
    assert response.json()["username"] == "cat"
    assert response.json()["email"] == "cat@gmail.com"