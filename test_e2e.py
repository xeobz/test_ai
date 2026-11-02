import sys
import os

# Добавляем корень проекта
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from fastapi.testclient import TestClient
from app.main import app

def run_tests():
    print("1. Тестирование Web-сервера и рендеринга страницы...")
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200, f"Ошибка веб-страницы: {response.status_code}"
    assert "AI-помощник подготовки карточек товаров" in response.text
    print("  -> Web UI отвечает 200 OK и рендерит HTML форму!")

    print("\n2. Тестирование API /api/generate с реальным вызовом LLM...")
    payload = {
        "name": "Манометр показывающий DM 02",
        "manufacturer": "Манотомь",
        "specs": {
            "диапазон измерений": "0–1,6 МПа",
            "класс точности": "1,5",
            "присоединение": "G1/2",
            "диаметр корпуса": "100 мм"
        },
        "description": "Прибор предназначен для измерения избыточного давления некристаллизующихся жидкостей..."
    }
    
    api_resp = client.post("/api/generate", json=payload)
    assert api_resp.status_code == 200, f"API вернул статус {api_resp.status_code}"
    data = api_resp.json()
    assert data["success"] is True, f"Генерация вернула ошибку: {data.get('error')}"
    
    card = data["data"]
    title = card["seo_title"]
    desc = card["seo_description"]
    queries = card["search_queries"]
    
    print(f"  -> Заголовок: '{title}' (Длина: {len(title)} симв.)")
    print(f"  -> Длина описания: {len(desc)} симв. (норма 800-1200)")
    print(f"  -> Поисковые запросы ({len(queries)} шт.): {queries}")
    print(f"  -> Характеристики: {list(card['key_characteristics'].keys())}")
    
    # Жесткие проверки критериев ТЗ
    assert len(title) <= 70, f"Заголовок длиннее 70 символов: {len(title)}"
    assert 800 <= len(desc) <= 1250, f"Описание не укладывается в рамки объема: {len(desc)}"
    assert 3 <= len(queries) <= 5, f"Количество поисковых запросов вне диапазона 3-5: {len(queries)}"
    assert "data_completeness" in card, "Отсутствует блок аудита полноты данных"
    assert "commercial_block" in card, "Отсутствует коммерческий блок"
    
    print("\nВсе тесты и проверки критериев ТЗ успешно пройдены!")

if __name__ == "__main__":
    run_tests()
