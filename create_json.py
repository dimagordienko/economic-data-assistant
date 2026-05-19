from pydantic import BaseModel, Field
from typing import Literal, Optional, List
import openai
from config import YANDEX_CLOUD_API_KEY, YANDEX_CLOUD_FOLDER, YANDEX_CLOUD_MODEL

client = openai.OpenAI(
  api_key=YANDEX_CLOUD_API_KEY,
  base_url="https://ai.api.cloud.yandex.net/v1",
  project=YANDEX_CLOUD_FOLDER
)

class QueryFilters(BaseModel):
    periodicity: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None

class QueryRouter(BaseModel):
    search_type: Literal["keyword", "vector", "hybrid"] = Field(
        description="Тип поиска: keyword для точных терминов, vector для смыслового, hybrid для комбинированного"
    )
    semantic_query: str = Field(
        description="Текст для векторного поиска (перефразированный запрос)"
    )
    keyword_query: List[str] = Field(
        default_factory=list,
        description="Массив ключевых слов для точного поиска"
    )
    filters: QueryFilters = Field(
        default_factory=QueryFilters,
        description="Фильтры по метаданным. periodicity (Периодичность) - Как часто обновляются данные - временной интервал между публикациями показателя"
    )

def requet_to_json_pydantic(user_request: str) -> dict:
    response = client.responses.parse(
        model=f"gpt://{YANDEX_CLOUD_FOLDER}/{YANDEX_CLOUD_MODEL}",
        instructions="""
        Ты query-router для поиска статистических показателей Fedstat.
        
        ВАЖНОЕ ПРАВИЛО:
        - Заполняй ТОЛЬКО ту информацию, которая ЯВНО указана в запросе пользователя
        - НЕ ДОДУМЫВАЙ даты, периодичность или другие параметры
        - Если пользователь не указал end_date - оставь None
        - Если пользователь не указал periodicity - оставь None
        - Если пользователь указал "с 2001 года" - это значит start_date = "2001", end_date = None
        
        Примеры:
        Запрос: "ввп россии с 2001 года"
        Правильно: start_date = "2001", end_date = None, periodicity = None
        
        Запрос: "ВВП России за 2002 год"
        Правильно: start_date = "2002", end_date = "2002", periodicity = None
        
        Запрос: "годовая динамика ВВП России 2010-2020"
        Правильно: periodicity = "yearly", start_date = "2010", end_date = "2020"
        
        search_type:
        - "keyword" - если запрос содержит точные термины (названия показателей, коды)
        - "vector" - если запрос смысловой, общий, описательный
        - "hybrid" - если нужны оба подхода
        
        semantic_query - перефразируй запрос для смыслового поиска (можно немного расширить)
        keyword_query - выдели ключевые слова (только то, что есть в запросе)
        
        НИЧЕГО НЕ ПРИДУМЫВАЙ. Если не хватает данных для заполнения поля - оставь None.
        """,
        input=user_request,
        text_format=QueryRouter,
    )
    return response.output_parsed.model_dump()

# Использование
# result = requet_to_json_pydantic("ВВП России за 2002 год в отношении к ВВП США")
# print(result)