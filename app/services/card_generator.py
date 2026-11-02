import logging
from typing import Dict, Any, Tuple
from app.schemas.product import ProductInput, ProductCardDraft
from app.services.llm_client import LLMClient
from app.services.prompts import SYSTEM_PROMPT, format_user_prompt

logger = logging.getLogger(__name__)

class CardGeneratorService:
    def __init__(self):
        self.llm_client = LLMClient()

    def _precheck_completeness(self, product: ProductInput) -> list[str]:
        """Локальная эвристическая проверка полноты данных до вызова LLM"""
        missing = []
        if not product.manufacturer:
            missing.append("Производитель прибора")
            
        # Проверяем характеристики в specs И в тексте описания вместе
        search_text = (product.description or "").lower() + " " + " ".join(product.specs.keys()).lower() + " " + " ".join(product.specs.values()).lower()
        
        has_range = any(w in search_text for w in ["диапазон", "предел", "кпа", "мпа", "бар", "°c", "мм рт"])
        has_accuracy = any(w in search_text for w in ["класс", "погрешност", "точност", "%"])
        has_connection = any(w in search_text for w in ["присоединен", "резьб", "монтаж", "фланец", "штуцер", "g1/", "м20"])
        
        if not has_range:
            missing.append("Диапазон измерений")
        if not has_accuracy:
            missing.append("Класс точности / погрешность")
        if not has_connection:
            missing.append("Тип присоединения к процессу")
            
        if not product.description or len(product.description.strip()) < 30:
            missing.append("Развернутое описание / выдержка из паспорта")
            
        return missing

    def format_as_markdown(self, card: ProductCardDraft, product_name: str) -> str:
        """Форматирует результат в удобный для контент-менеджера Markdown"""
        specs_md = "\n".join([f"- **{k}**: {v}" for k, v in card.key_characteristics.items()])
        queries_md = "\n".join([f"- `{q}`" for q in card.search_queries])
        
        status_badge = "✅ **Данные полные**" if card.data_completeness.is_sufficient else "⚠️ **Требуются уточнения**"
        
        missing_md = ""
        if card.data_completeness.missing_fields:
            missing_items = "\n".join([f"  - {f}" for f in card.data_completeness.missing_fields])
            missing_md = f"\n**Недостающие поля для запроса у поставщика:**\n{missing_items}\n"
            
        md = f"""# Черновик карточки товара: {product_name}

## 1. SEO-заголовок (Title)
> {card.seo_title}
*(Длина: {len(card.seo_title)} символов)*

---

## 2. SEO-описание (Description / Текст карточки)
{card.seo_description}

*(Длина: {len(card.seo_description)} символов)*

---

## 3. Ключевые технические характеристики
{specs_md}

---

## 4. Рекомендуемые поисковые запросы (SEO)
{queries_md}

---

## 5. Коммерческий блок (для отдела продаж)
* **Целевая аудитория и отрасли:** {card.commercial_block.target_audience}
* **Решаемые технологические задачи:** {card.commercial_block.tasks_solved}

---

## 6. Отчет о полноте данных
{status_badge}
{missing_md}
*Примечание:* {card.data_completeness.notes or "Все ключевые поля заполнены корректно."}
"""
        return md

    async def generate_card(self, product: ProductInput) -> Tuple[ProductCardDraft, str]:
        """Генерирует карточку товара и возвращает модель + markdown представление"""
        # Предварительный анализ пропусков
        pre_missing = self._precheck_completeness(product)
        
        user_prompt = format_user_prompt(product.model_dump())
        raw_json = await self.llm_client.generate_json(SYSTEM_PROMPT, user_prompt)
        
        # Валидируем через Pydantic
        card = ProductCardDraft.model_validate(raw_json)
        
        # Защитная постобработка SEO-заголовка (жесткий лимит до 70 символов)
        if len(card.seo_title) > 70:
            # Обрезаем по последнему слову до 70 символов
            truncated = card.seo_title[:67]
            if " " in truncated:
                truncated = truncated.rsplit(" ", 1)[0]
            card.seo_title = truncated.rstrip(",. -")

        # Объединяем детекцию пропусков
        combined_missing = list(set(card.data_completeness.missing_fields + pre_missing))
        if combined_missing:
            card.data_completeness.missing_fields = sorted(combined_missing)
            if len(combined_missing) >= 3:
                card.data_completeness.is_sufficient = False
                
        # Генерируем Markdown
        markdown_text = self.format_as_markdown(card, product.name)
        return card, markdown_text
