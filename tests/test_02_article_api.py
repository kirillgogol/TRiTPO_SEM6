from fastapi.testclient import TestClient
import json
from test_01_users_api import USER_DATA

def get_user_token(client: TestClient, user_data):
    response = client.post('/auth/login', data=user_data)
    token = response.json()['access_token']
    return token


def test_create_article(client: TestClient):
    token = get_user_token(client, USER_DATA)

    data = {
    "title":"ARTICLE 1", 
    "brief_description":"About python", 
    "url":"https://app.clockify.me/tracker",
    "language": "English",
    "category": "python"
    }

    response = client.post("/article/", params=data, files=None, headers={'Authorization': f'Bearer {token}'})
    
    assert response.status_code == 201
    assert response.json()["title"] == "ARTICLE 1"


def test_get_all_articles(client: TestClient):

    token = get_user_token(client, USER_DATA)

    response = client.get(f"/article/", headers={'Authorization': f'Bearer {token}'})
    
    assert response.status_code == 200
    len(response.json()) == 1


def test_get_article(client: TestClient):

    article_id = 1

    token = get_user_token(client, USER_DATA)

    response = client.get(f"/article/{article_id}", headers={'Authorization': f'Bearer {token}'})
    
    assert response.status_code == 200
    assert response.json()["title"] == "ARTICLE 1"


def test_update_article(client: TestClient):

    token = get_user_token(client, USER_DATA)

    article_id = 1

    data = {
    "title":"ARTICLE 1 upd", 
    "brief_description":"About python", 
    "url":"https://app.clockify.me/tracker",
    "language": "English",
    "category": "python"
    }

    response = client.put(f"/article/{article_id}", data=json.dumps(data), 
    headers={'Authorization': f'Bearer {token}'})
    
    assert response.status_code == 202
    assert response.json()["title"] == "ARTICLE 1 upd"


def test_delete_article(client: TestClient):

    token = get_user_token(client, USER_DATA)

    article_id = 1

    response = client.delete(f"/article/{article_id}", headers={'Authorization': f'Bearer {token}'})
    
    assert response.status_code == 204
