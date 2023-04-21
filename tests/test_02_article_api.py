from fastapi.testclient import TestClient
import json
from test_01_users_api import USER_DATA, USER_DATA_FOR_UNOTHORIZED_ACCESS


def test_create_article(client: TestClient, token):

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


def test_create_article_without_url_and_file(client: TestClient, token):

    data = {
    "title":"ARTICLE 2", 
    "brief_description":"About python", 
    "url": "",
    "language": "English",
    "category": "python"
    }

    response = client.post("/article/", params=data, files=None, headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == 400
    assert response.json()["detail"] == "Article url and file should not be empty or full at the same time"


def test_get_all_articles(client: TestClient, token):

    response = client.get(f"/article/all", headers={'Authorization': f'Bearer {token}'})
    
    assert response.status_code == 200
    len(response.json()) == 1


def test_get_article(client: TestClient, token):
    article_id = 1
    response = client.get(f"/article/{article_id}", headers={'Authorization': f'Bearer {token}'})
    
    assert response.status_code == 200
    assert response.json()["title"] == "ARTICLE 1"


def test_get_article_by_wrong_id(client: TestClient, token):
    article_id = 1000

    response = client.get(f"/article/{article_id}", headers={'Authorization': f'Bearer {token}'})
    
    assert response.status_code == 404
    assert response.json()["detail"] == f'Article with id={article_id} is not found'


def test_update_article(client: TestClient, token):

    article_id = 1

    data = {
    "title":"ARTICLE 1 upd", 
    "brief_description":"About python", 
    "url":"https://app.clockify.me/tracker",
    "language": "English",
    "category": "python"
    }

    response = client.put(f"/article/{article_id}", params=data, 
    headers={'Authorization': f'Bearer {token}'})
    
    assert response.status_code == 202
    assert response.json()["title"] == "ARTICLE 1 upd"


def test_update_article_by_wrong_id(client: TestClient, token):
    article_id = 10000

    data = {
    "title":"ARTICLE 1 upd", 
    "brief_description":"About python", 
    "url":"https://app.clockify.me/tracker",
    "language": "English",
    "category": "python"
    }

    response = client.put(f"/article/{article_id}", params=data, 
    headers={'Authorization': f'Bearer {token}'})
    
    assert response.status_code == 404
    assert response.json()["detail"] == f'Article with id={article_id} is not found'


def test_update_article_by_unothorizated_user(client: TestClient, unothorized_access_token):
    article_id = 1

    data = {
    "title":"ARTICLE 1 upd", 
    "brief_description":"About python", 
    "url":"https://app.clockify.me/tracker",
    "language": "English",
    "category": "python"
    }

    response = client.put(f"/article/{article_id}", params=data, 
    headers={'Authorization': f'Bearer {unothorized_access_token}'})
    
    assert response.status_code == 403
    assert response.json()["detail"] == f'Updating provides only for author of the article with id={article_id}'


def test_delete_article_by_wrong_id(client: TestClient, token):
    article_id = 10000
    response = client.delete(f"/article/{article_id}", headers={'Authorization': f'Bearer {token}'})
    
    assert response.status_code == 404
    assert response.json()["detail"] == f'Article with id={article_id} is not found'


def test_delete_article_by_unothorizated_user(client: TestClient, unothorized_access_token):
    article_id = 1
    response = client.delete(f"/article/{article_id}", headers={'Authorization': f'Bearer {unothorized_access_token}'})
    
    assert response.status_code == 403
    assert response.json()["detail"] == f'Deleting provides only for author of the article with id={article_id}'


def test_delete_article(client: TestClient, token):
    article_id = 1
    response = client.delete(f"/article/{article_id}", headers={'Authorization': f'Bearer {token}'})
    
    assert response.status_code == 204
