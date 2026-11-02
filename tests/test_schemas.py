import pytest
from app.schemas.product import ProductInput, ProductCardDraft

def test_product_input_validation():
    # Валидный ввод
    p = ProductInput(name="Манометр DM 02", manufacturer="Манотомь")
    assert p.name == "Манометр DM 02"
    assert p.manufacturer == "Манотомь"
    
    # Пустое имя должно вызывать ошибку
    with pytest.raises(Exception):
        ProductInput(name="   ")

def test_product_card_draft_schema():
    sample_data = {
        "seo_title": "Манометр DM 02 — купить для B2B",
        "seo_description": "Описание прибора более 800 символов... " * 30,
        "key_characteristics": {
            "Диапазон": "0-1.6 МПа",
            "Питание": "данных нет"
        },
        "search_queries": [
            "манометр dm 02",
            "манометр купить b2b",
            "манометры оптом"
        ],
        "commercial_block": {
            "target_audience": "ЖКХ, энергетика",
            "tasks_solved": "Контроль давления"
        },
        "data_completeness": {
            "is_sufficient": True,
            "missing_fields": [],
            "notes": "Данные полные"
        }
    }
    card = ProductCardDraft.model_validate(sample_data)
    assert card.seo_title == "Манометр DM 02 — купить для B2B"
    assert len(card.search_queries) == 3
    assert card.key_characteristics["Питание"] == "данных нет"
