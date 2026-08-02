from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_docs_page():
    response = client.get("/docs")
    assert response.status_code == 200


def test_openapi_json():
    response = client.get("/openapi.json")
    assert response.status_code == 200