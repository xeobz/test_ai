import pytest
from app.schemas.product import ProductInput
from app.services.card_generator import CardGeneratorService

def test_precheck_completeness():
    service = CardGeneratorService()
    
    # Полный товар
    full_product = ProductInput(
        name="Манометр DM 02",
        manufacturer="Манотомь",
        specs={
            "диапазон измерений": "0-1.6 МПа",
            "класс точности": "1.5",
            "присоединение": "G1/2"
        },
        description="Развернутое описание прибора для промышленных систем трубопроводов."
    )
    missing = service._precheck_completeness(full_product)
    assert len(missing) == 0

    # Неполный товар
    incomplete_product = ProductInput(
        name="Датчик ТСП",
        manufacturer=None,
        specs={"диаметр": "6 мм"},
        description="Коротко"
    )
    missing_incomplete = service._precheck_completeness(incomplete_product)
    assert "Производитель прибора" in missing_incomplete
    assert "Диапазон измерений" in missing_incomplete
    assert "Класс точности / погрешность" in missing_incomplete
