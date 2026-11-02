from typing import Dict, List, Optional
from pydantic import BaseModel, Field, field_validator

class ProductInput(BaseModel):
    name: str = Field(..., description="Название товара (прибора)", min_length=2)
    manufacturer: Optional[str] = Field(None, description="Производитель")
    specs: Dict[str, str] = Field(default_factory=dict, description="Краткие характеристики")
    description: Optional[str] = Field(None, description="Текстовое описание или фрагмент паспорта")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        clean = v.strip()
        if not clean:
            raise ValueError("Название товара не может быть пустым")
        return clean

class CommercialBlock(BaseModel):
    target_audience: str = Field(..., description="Кому подходит прибор (отрасли, специалисты)")
    tasks_solved: str = Field(..., description="Какие практические задачи решает прибор")

class MissingDataReport(BaseModel):
    is_sufficient: bool = Field(..., description="Достаточно ли данных для полной карточки")
    missing_fields: List[str] = Field(default_factory=list, description="Отсутствующие или рекомендуемые к уточнению поля")
    notes: Optional[str] = Field(None, description="Пояснения для контент-менеджера")

class ProductCardDraft(BaseModel):
    seo_title: str = Field(..., description="SEO-заголовок (до 70 символов)")
    seo_description: str = Field(..., description="SEO-описание (объёмом 800–1200 символов)")
    key_characteristics: Dict[str, str] = Field(..., description="Структурированный список ключевых характеристик")
    search_queries: List[str] = Field(..., description="3–5 поисковых запросов для SEO-оптимизации")
    commercial_block: CommercialBlock = Field(..., description="Коммерческий блок для менеджера по продажам")
    data_completeness: MissingDataReport = Field(..., description="Отчет о полноте данных и недостающих полях")

class GenerationResponse(BaseModel):
    success: bool
    data: Optional[ProductCardDraft] = None
    markdown: Optional[str] = None
    error: Optional[str] = None
