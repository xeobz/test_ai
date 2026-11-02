from fastapi.testclient import TestClient
from app.main import app

def test_web_ui_renders_html():
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert "AI-помощник подготовки карточек товаров" in response.text
    assert "Манометр показывающий DM 02" in response.text

def test_api_validation_error_on_empty_name():
    client = TestClient(app)
    # Пустое имя должно вызывать валидацию 422
    response = client.post("/api/generate", json={"name": "   "})
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data
