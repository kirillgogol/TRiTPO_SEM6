from fastapi.testclient import TestClient
import json


ACCESS_USERNAME = "cat@gmail.com"
ACCESS_PASSWORD = "123456"

UNITHORIZED_ACCESS_USERNAME = "cat3@gmail.com"
UNITHORIZED_ACCESS_PASSWORD = "33333333"

USER_DATA = {
    'username': ACCESS_USERNAME,
    'password': ACCESS_PASSWORD,
}

USER_DATA_FOR_UNOTHORIZED_ACCESS = {
    "username":UNITHORIZED_ACCESS_USERNAME,
    "password":UNITHORIZED_ACCESS_PASSWORD,
}


def get_user_token(client: TestClient, user_data):
    response = client.post('/auth/login', data=user_data)
    token = response.json()['access_token']
    return token


def test_create_user(client: TestClient):
    data = {"username":"cat", "email":ACCESS_USERNAME, "password":ACCESS_PASSWORD}
    response = client.post("/user/", data=json.dumps(data))
    
    assert response.status_code == 201
    assert response.json()["username"] == "cat"
    assert response.json()["email"] == ACCESS_USERNAME

    data = {"username":"cat2", "email":"cat2@gmail.com", "password":"12345678"}

    response = client.post("/user/", data=json.dumps(data))
    
    assert response.status_code == 201
    assert response.json()["username"] == "cat2"
    assert response.json()["email"] == "cat2@gmail.com"

    data = {"username":"cat3", "email":UNITHORIZED_ACCESS_USERNAME, "password":UNITHORIZED_ACCESS_PASSWORD}

    response = client.post("/user/", data=json.dumps(data))
    
    assert response.status_code == 201
    assert response.json()["username"] == "cat3"
    assert response.json()["email"] == UNITHORIZED_ACCESS_USERNAME


def test_create_user_with_existing_email(client: TestClient):
    data = {"username":"cat31", "email":"cat2@gmail.com", "password":"1234560000"}
    response = client.post("/user/", data=json.dumps(data))
    
    assert response.status_code == 400
    assert response.json()["detail"] == f"User with email {data['email']} is already exist"


def test_get_all_users(client: TestClient):
    token = get_user_token(client, USER_DATA)

    response = client.get("/user/all", headers={'Authorization': f'Bearer {token}'})
    
    assert response.status_code == 200
    assert len(response.json()) == 3


def test_get_user_by_id(client: TestClient):
    user_id = 2

    token = get_user_token(client, USER_DATA)

    response = client.get(f"/user/{user_id}", headers={'Authorization': f'Bearer {token}'})
    
    assert response.status_code == 200
    assert response.json()['username'] == 'cat2'
    assert response.json()["email"] == "cat2@gmail.com"


def test_get_user_by_wrong_id(client: TestClient):
    user_id = 1000
    token = get_user_token(client, USER_DATA)

    response = client.get(f"/user/{user_id}", headers={'Authorization': f'Bearer {token}'})
    
    assert response.status_code == 404
    assert response.json()['detail'] == f'User with id={user_id} is not found'


def test_update_user(client: TestClient):
    user_id = 2

    token = get_user_token(client, USER_DATA)

    data_for_update = {
        'username': 'new_cat2',
        'email': 'new_cat2@gmail.com',
        'password': '12345new',
    }

    response = client.put(
        f"/user/{user_id}", 
        headers={'Authorization': f'Bearer {token}'}, 
        data=json.dumps(data_for_update)
    )
    
    assert response.status_code == 202
    assert response.json()['username'] == 'new_cat2'
    assert response.json()["email"] == "new_cat2@gmail.com"


def test_update_user_by_wrong_id(client: TestClient):
    user_id = 1000

    token = get_user_token(client, USER_DATA)

    data_for_update = {
        'username': 'new_cat2',
        'email': 'new_cat2@gmail.com',
        'password': '12345new',
    }

    response = client.put(
        f"/user/{user_id}", 
        headers={'Authorization': f'Bearer {token}'}, 
        data=json.dumps(data_for_update)
    )
    
    assert response.status_code == 404
    assert response.json()['detail'] == f'User with id={user_id} is not found'


def test_update_user_with_existing_email(client: TestClient):
    user_id = 2

    token = get_user_token(client, USER_DATA)

    data_for_update = {
        'username': 'new_cat2',
        'email': 'cat@gmail.com',
        'password': '12345new',
    }

    response = client.put(
        f"/user/{user_id}", 
        headers={'Authorization': f'Bearer {token}'}, 
        data=json.dumps(data_for_update)
    )
    
    assert response.status_code == 400
    assert response.json()['detail'] == f"User with email {data_for_update['email']} is already exist"


def test_delete_user_by_id(client: TestClient):
    user_id = 2

    token = get_user_token(client, USER_DATA)

    response = client.delete(
        f"/user/{user_id}", 
        headers={'Authorization': f'Bearer {token}'}
    )
    
    assert response.status_code == 200
    assert response.json()['detail'] == f"User with id={user_id} was successfully deleted"


def test_delete_user_by_wrong_id(client: TestClient):
    user_id = 2

    token = get_user_token(client, USER_DATA)

    response = client.delete(
        f"/user/{user_id}", 
        headers={'Authorization': f'Bearer {token}'}
    )
    
    assert response.status_code == 404
    assert response.json()['detail'] == f'User with id={user_id} is not found'
    