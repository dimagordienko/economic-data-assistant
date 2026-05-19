# def check_full_request(json) -> bool:
#     for k,v in json.items:
#         if v == None:
#             print(f'Не хватает данных {k}')
#     for k,v in json['filters']:
#         if v == None:
#             print(f'Не хватает данных {k}')
            
#     print(json)


import openai
from pydantic import BaseModel, Field
from typing import Optional, List
from config import YANDEX_CLOUD_API_KEY, YANDEX_CLOUD_FOLDER, YANDEX_CLOUD_MODEL

client = openai.OpenAI(
    api_key=YANDEX_CLOUD_API_KEY,
    base_url="https://ai.api.cloud.yandex.net/v1",
    project=YANDEX_CLOUD_FOLDER
)

class QueryCompleteness(BaseModel):
    is_complete: bool = Field(
        description="True - если запрос содержит все необходимые компоненты для поиска, False - если чего-то не хватает"
    )
    # missing_fields: List[str] = Field(
    #     default_factory=list,
    #     description="Список того, чего не хватает в запросе (например: ['страна для сравнения', 'конечный год', 'периодичность'])"
    # )
    suggestion: str = Field(
        description="Понятное пользователю сообщение о том, чего не хватает и как исправить запрос"
    )

def check_full_request(user_request) -> tuple[bool, str]:
    response = client.responses.parse(
        model=f"gpt://{YANDEX_CLOUD_FOLDER}/{YANDEX_CLOUD_MODEL}",
        instructions="""
        Ты - валидатор запросов к базе статистических данных Fedstat.
        
        Проверь, достаточно ли информации в запросе для однозначного поиска данных.
        
        ЧТО ПРОВЕРЯТЬ:
        1. Временной период:
           - Если запрос про динамику - нужны start_date И end_date
           - Если "с 2001 года" - есть start_date, но нет end_date → НЕ ПОЛНЫЙ
           - Если "за 2002 год" - есть конкретный год → ПОЛНЫЙ
           - Если "за 2002-2024" - есть оба года → ПОЛНЫЙ
        
        2. Периодичность (если важна):
           - "годовая", "квартальная", "месячная" - если не указана, но важна → НЕ ПОЛНЫЙ
           - Для ВВП обычно годовая, можно не требовать
        
        3. Объекты анализа:
           - Если сравнение - нужны ОБЕ страны (например "ВВП России и США")
           - Если "ВВП России" - достаточно одной страны
           - Если "ВВП Европы" - слишком размыто, нужны конкретные страны
        
        4. Показатели:
           - "ВВП", "инфляция", "безработица" - конкретный показатель должен быть
           - Если "экономические показатели" - НЕ ПОЛНЫЙ
        
        5. Единицы измерения (если важны):
           - "в долларах", "в рублях", "ППС" - если не указано, но важно - отметить
        
        ПРИМЕРЫ:
        
        Запрос: "ВВП России с 2001 года"
        is_complete: False
        missing_fields: ["конечный год"]
        suggestion: "В запросе указан начальный год (2001), но не указан конечный. Уточните период: например, 'ВВП России с 2001 по 2024 год'"
        
        Запрос: "ВВП России за 2002 год"
        is_complete: True
        missing_fields: []
        suggestion: ""
        
        Запрос: "Сравни ВВП России"
        is_complete: False
        missing_fields: ["страна для сравнения"]
        suggestion: "Для сравнения нужна вторая страна. Например: 'сравни ВВП России и США'"
        
        Запрос: "Покажи годовую динамику ВВП России"
        is_complete: False
        missing_fields: ["период (начальный и конечный год)"]
        suggestion: "Укажите временной период. Например: 'годовая динамика ВВП России с 2010 по 2020 год'"
        
        Запрос: "ВВП России в долларах за 2020-2023"
        is_complete: True
        missing_fields: []
        suggestion: ""
        
        Запрос: "Экономика России"
        is_complete: False
        missing_fields: ["конкретный показатель"]
        suggestion: "Уточните, какой показатель вас интересует: ВВП, инфляция, безработица и т.д."
        
        ВАЖНО: 
        - Будь внимателен к контексту
        - Если запрос уже полный - is_complete = True
        - suggestion должен быть понятным и конкретным
        - Не додумывай то, чего нет в запросе
        """,
        input=f"Вот запрос пользователя: {user_request}",
        text_format=QueryCompleteness,
    )
    
    result = response.output_parsed
    return result.is_complete, result.suggestion

# temp = check_full_request('Покажи динамику инфляции в России (индекс потребительских цен) за 2014–2024 годы, годовые значения.')
# if temp[0]:
#     print('Запрос верный')
# else:
#     print(temp[1])