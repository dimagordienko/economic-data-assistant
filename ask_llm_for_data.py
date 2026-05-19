import openai
from pydantic import BaseModel, Field
from config import YANDEX_CLOUD_API_KEY, YANDEX_CLOUD_FOLDER, YANDEX_CLOUD_MODEL

client = openai.OpenAI(
    api_key=YANDEX_CLOUD_API_KEY,
    base_url="https://ai.api.cloud.yandex.net/v1",
    project=YANDEX_CLOUD_FOLDER
)

class NeedMoreData(BaseModel):
    need_more_data: bool = Field(
        description="True - если для ответа на вопрос нужны дополнительные данные, False - если информации достаточно"
    )
    reason: str = Field(
        description="""КРИТИЧЕСКИ ВАЖНО: Если need_more_data=True, reason должен содержать ТОЛЬКО поисковый запрос из 3-7 слов.
        НИКАКИХ объяснений, НИКАКИХ рассуждений, НИКАКИХ вводных фраз.
        Только ключевые слова через пробел.
        
        ПРАВИЛЬНО: "ВВП Россия США 2002 сравнение"
        НЕПРАВИЛЬНО: "Для сравнения нужны данные по ВВП России и США за 2002 год"
        
        Если need_more_data=False, верни пустую строку."""
    )

def is_requared_data(user_request: str, data: list) -> tuple[bool, str]:
    response = client.responses.parse(
        model=f"gpt://{YANDEX_CLOUD_FOLDER}/{YANDEX_CLOUD_MODEL}",
        instructions=(
            "Ты - аналитик данных. Твоя задача - определить, хватает ли данных для ответа.\n"
            "ВАЖНО: Если данных НЕ хватает, в поле reason напиши ТОЛЬКО короткий поисковый запрос (3-7 слов).\n"
            "ЗАПРЕЩЕНО писать объяснения, рассуждения или вводные фразы в reason.\n"
            "Пример правильного reason: 'ВВП Россия 2002'\n"
            "Пример неправильного reason: 'Для ответа нужны данные по ВВП России за 2002 год'\n\n"
            "Отвечай строго по формату Pydantic."
        ),
        input=f"Запрос пользователя: {user_request}\n\nДоступные данные: {data if data else 'Нет данных'}",
        text_format=NeedMoreData,
    )
    
    result = response.output_parsed
    
    # Дополнительная очистка reason, если модель всё равно добавила лишнее
    if result.need_more_data and result.reason:
        # Очищаем от типичных фраз
        import re
        clean_reason = result.reason
        # Удаляем распространённые вводные фразы
        phrases_to_remove = [
            r'нужны? данные? (?:по|о|для|на)',
            r'требуютс[яь]',
            r'не хватает',
            r'отсутствуют',
            r'необходимо найти',
            r'следует найти',
            r'поищи',
            r'найди',
            r'данные (?:по|о|для|на)',
            r'информация (?:по|о|для|на)',
            r'показатели (?:по|о|для|на)',
            r'Для (?:корректного|полного|точного)',
            r'Без (?:абсолютных|точных|конкретных)',
            r'Также требуется',
        ]
        for phrase in phrases_to_remove:
            clean_reason = re.sub(phrase, '', clean_reason, flags=re.IGNORECASE)
        
        # Обрезаем лишние слова в конце
        clean_reason = re.sub(r'[.,;:?!]$', '', clean_reason)
        clean_reason = clean_reason.strip()
        
        # Оставляем только первые 7 слов
        words = clean_reason.split()
        if len(words) > 7:
            clean_reason = ' '.join(words[:7])
        
        # Если после очистки пусто - используем оригинальный запрос
        if not clean_reason:
            clean_reason = user_request[:50]
            
        result.reason = clean_reason
    
    return result.need_more_data, result.reason