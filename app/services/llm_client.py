import json
import logging
from typing import Dict, Any
import httpx
from app.core.config import settings

logger = logging.getLogger(__name__)

class LLMClientError(Exception):
    pass

class LLMClient:
    def __init__(self):
        self.provider = settings.LLM_PROVIDER
        if self.provider == "openrouter":
            self.api_key = settings.OPENROUTER_API_KEY
            self.base_url = settings.OPENROUTER_BASE_URL
            self.model = settings.OPENROUTER_MODEL
        else:
            self.api_key = settings.OPENAI_API_KEY
            self.base_url = settings.OPENAI_BASE_URL
            self.model = settings.OPENAI_MODEL
            
        if not self.api_key:
            logger.warning(f"API key for provider '{self.provider}' is not configured!")

    async def generate_json(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        if not self.api_key:
            raise LLMClientError(
                f"API-ключ для провайдера '{self.provider}' не задан. "
                f"Укажите ключ в файле .env (OPENROUTER_API_KEY или OPENAI_API_KEY)."
            )

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        if self.provider == "openrouter":
            headers["HTTP-Referer"] = "https://github.com/ai-product-card-generator"
            headers["X-Title"] = "AI Product Card Generator"

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.2, # Низкая температура для минимизации галлюцинаций и строгого следования фактам
            "response_format": {"type": "json_object"}
        }

        # Выполняем запрос с повторными попытками (retry logic)
        max_retries = 3
        last_error = None
        
        for attempt in range(1, max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=settings.REQUEST_TIMEOUT) as client:
                    response = await client.post(
                        f"{self.base_url}/chat/completions",
                        headers=headers,
                        json=payload
                    )
                    
                    if response.status_code != 200:
                        error_detail = response.text
                        logger.error(f"LLM API Error (status {response.status_code}): {error_detail}")
                        raise LLMClientError(f"Ошибка API LLM ({response.status_code}): {error_detail}")
                        
                    data = response.json()
                    content = data["choices"][0]["message"]["content"]
                    
                    # Очистка возможных markdown-тегов
                    content = content.strip()
                    if content.startswith("```json"):
                        content = content[7:]
                    if content.startswith("```"):
                        content = content[3:]
                    if content.endswith("```"):
                        content = content[:-3]
                    content = content.strip()
                    
                    parsed_json = json.loads(content)
                    return parsed_json
                    
            except (httpx.TimeoutException, httpx.NetworkError) as net_err:
                last_error = net_err
                logger.warning(f"Сетевой сбой при вызове LLM (попытка {attempt}/{max_retries}): {net_err}")
                if attempt == max_retries:
                    raise LLMClientError(f"Превышено время ожидания ответа от LLM API после {max_retries} попыток: {net_err}")
            except json.JSONDecodeError as json_err:
                logger.error(f"LLM вернула некорректный JSON: {content}")
                raise LLMClientError(f"Ошибка парсинга JSON ответа модели: {json_err}")
            except Exception as e:
                if isinstance(e, LLMClientError):
                    raise
                raise LLMClientError(f"Непредвиденная ошибка при обращении к LLM: {str(e)}")

        raise LLMClientError(f"Не удалось получить ответ от LLM: {last_error}")
