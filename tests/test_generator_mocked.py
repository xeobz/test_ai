import asyncio
from unittest.mock import AsyncMock, patch
from app.schemas.product import ProductInput
from app.services.card_generator import CardGeneratorService

def test_card_generator_success_mocked():
    """Тест бизнес-логики генератора без обращения к реальному платному API"""
    mock_llm_response = {
        "seo_title": "Манометр DM 02 Манотомь — купить для B2B",
        "seo_description": ("Промышленный манометр для точного контроля давления в трубопроводах и котельных. " * 12)[:950],
        "key_characteristics": {
            "Диапазон измерений": "0–1,6 МПа",
            "Класс точности": "1,5",
            "Присоединение": "G1/2"
        },
        "search_queries": [
            "манометр dm 02 купить",
            "манометры манотомь оптом",
            "манометр показывающий характеристики"
        ],
        "commercial_block": {
            "target_audience": "ЖКХ, энергетика, промышленные котельные",
            "tasks_solved": "Контроль давления неагрессивных сред"
        },
        "data_completeness": {
            "is_sufficient": True,
            "missing_fields": [],
            "notes": "Данные полные"
        }
    }
    
    with patch("app.services.card_generator.LLMClient.generate_json", new_callable=AsyncMock) as mock_generate:
        mock_generate.return_value = mock_llm_response
        
        service = CardGeneratorService()
        product = ProductInput(
            name="Манометр показывающий DM 02",
            manufacturer="Манотомь",
            specs={
                "диапазон измерений": "0–1,6 МПа",
                "класс точности": "1,5",
                "присоединение": "G1/2"
            },
            description="Прибор для измерения давления некристаллизующихся сред."
        )
        
        card, md = asyncio.run(service.generate_card(product))
        
        assert card.seo_title == "Манометр DM 02 Манотомь — купить для B2B"
        assert len(card.seo_title) <= 70
        assert 800 <= len(card.seo_description) <= 1200
        assert len(card.search_queries) == 3
        assert "# Черновик карточки товара: Манометр показывающий DM 02" in md
