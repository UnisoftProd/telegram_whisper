from docx import Document
import asyncio
from googletrans import Translator

async def translate_docx(input_file, output_file, target_language='ru'):
    # Создаем объект документа
    doc = Document(input_file)
    async with Translator() as translator:
    # Перебираем все параграфы в документе
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():  # Пропускаем пустые строки
                # Переводим текст параграфа
                translated_text = await translator.translate(paragraph.text, dest=target_language)
                paragraph.text = translated_text.text

    # Сохраняем переведенный документ
    doc.save(output_file)
    print(f"Документ переведен и сохранен в {output_file}")



