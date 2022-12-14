from fastapi.testclient import TestClient
import json


def get_user_token(client: TestClient, user_data):
    response = client.post('/auth/login', data=user_data)
    token = response.json()['access_token']
    return token


def test_create_user(client: TestClient):
    data = {"username":"cat", "email":"cat@gmail.com", "password":"1234"}
    response = client.post("/user/", data=json.dumps(data))
    
    assert response.status_code == 201
    assert response.json()["username"] == "cat"
    assert response.json()["email"] == "cat@gmail.com"

    data = {"username":"cat2", "email":"cat2@gmail.com", "password":"12345"}

    response = client.post("/user/", data=json.dumps(data))
    
    assert response.status_code == 201
    assert response.json()["username"] == "cat2"
    assert response.json()["email"] == "cat2@gmail.com"


def test_get_all_users(client: TestClient):

    user_data = {
        'username': 'cat@gmail.com',
        'password': '1234',
    }
    token = get_user_token(client, user_data)

    response = client.get("/user/all", headers={'Authorization': f'Bearer {token}'})
    
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_user_by_id(client: TestClient):
    user_id = 2
    user_data = {
        'username': 'cat@gmail.com',
        'password': '1234',
    }
    token = get_user_token(client, user_data)

    response = client.get(f"/user/{user_id}", headers={'Authorization': f'Bearer {token}'})
    
    assert response.status_code == 200
    assert response.json()['username'] == 'cat2'
    assert response.json()["email"] == "cat2@gmail.com"


def test_get_user_by_wrong_id(client: TestClient):
    user_id = 1000
    user_data = {
        'username': 'cat@gmail.com',
        'password': '1234',
    }
    token = get_user_token(client, user_data)

    response = client.get(f"/user/{user_id}", headers={'Authorization': f'Bearer {token}'})
    
    assert response.status_code == 404
    assert response.json()['detail'] == f'User with id={user_id} not found'


def test_update_user_by_wrong_id(client: TestClient):
    user_id = 2
    user_data = {
        'username': 'cat@gmail.com',
        'password': '1234',
    }
    token = get_user_token(client, user_data)

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
    user_data = {
        'username': 'cat@gmail.com',
        'password': '1234',
    }
    token = get_user_token(client, user_data)

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
    assert response.json()['detail'] == f'User with id={user_id} not found'


def test_delete_user_by_id(client: TestClient):
    user_id = 2
    user_data = {
        'username': 'cat@gmail.com',
        'password': '1234',
    }
    token = get_user_token(client, user_data)

    response = client.delete(
        f"/user/{user_id}", 
        headers={'Authorization': f'Bearer {token}'}
    )
    
    assert response.status_code == 200
    assert response.json()['detail'] == f"User with id={user_id} was successfully deleted"


def test_delete_user_by_wrong_id(client: TestClient):
    user_id = 2
    user_data = {
        'username': 'cat@gmail.com',
        'password': '1234',
    }
    token = get_user_token(client, user_data)

    response = client.delete(
        f"/user/{user_id}", 
        headers={'Authorization': f'Bearer {token}'}
    )
    
    assert response.status_code == 404
    assert response.json()['detail'] == f'User with id={user_id} not found'