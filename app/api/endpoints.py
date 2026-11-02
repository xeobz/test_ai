import os
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.schemas.product import ProductInput, GenerationResponse
from app.services.card_generator import CardGeneratorService
from app.services.llm_client import LLMClientError

router = APIRouter()

templates_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
templates = Jinja2Templates(directory=templates_dir)

generator_service = CardGeneratorService()

@router.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    """Веб-интерфейс для контент-менеджера"""
    return templates.TemplateResponse(request, "index.html")

@router.post("/api/generate", response_model=GenerationResponse)
async def generate_product_card(product: ProductInput):
    """API-эндпоинт генерации черновика карточки товара"""
    try:
        card, markdown_text = await generator_service.generate_card(product)
        return GenerationResponse(
            success=True,
            data=card,
            markdown=markdown_text
        )
    except LLMClientError as e:
        return GenerationResponse(
            success=False,
            error=str(e)
        )
    except Exception as e:
        return GenerationResponse(
            success=False,
            error=f"Внутренняя ошибка сервиса: {str(e)}"
        )
