import argparse
import asyncio
import json
import os
import sys

# Настройка UTF-8 для вывода в консоль Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

# Добавляем корневую директорию проекта в sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.schemas.product import ProductInput
from app.services.card_generator import CardGeneratorService

async def process_file(file_path: str, output_format: str):
    if not os.path.exists(file_path):
        print(f"Ошибка: Файл '{file_path}' не найден!")
        sys.exit(1)
        
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Ошибка чтения JSON из файла: {e}")
        sys.exit(1)
        
    try:
        product = ProductInput.model_validate(data)
    except Exception as e:
        print(f"Ошибка валидации входных данных: {e}")
        sys.exit(1)
        
    print(f"Обработка прибора: {product.name} ({product.manufacturer or 'Производитель не указан'})...")
    service = CardGeneratorService()
    
    try:
        card, markdown_text = await service.generate_card(product)
        print("\n" + "="*60)
        print("РЕЗУЛЬТАТ ГЕНЕРАЦИИ:")
        print("="*60 + "\n")
        
        if output_format == "markdown":
            print(markdown_text)
        else:
            print(json.dumps(card.model_dump(), ensure_ascii=False, indent=2))
            
    except Exception as e:
        print(f"Ошибка генерации: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="CLI генератор карточек товаров B2B")
    parser.add_argument("--file", "-f", required=True, help="Путь к JSON-файлу с данными товара")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown", help="Формат вывода (markdown или json)")
    
    args = parser.parse_args()
    asyncio.run(process_file(args.file, args.format))

if __name__ == "__main__":
    main()
