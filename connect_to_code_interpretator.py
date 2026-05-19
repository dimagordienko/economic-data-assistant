import openai
from pathlib import Path
import pandas as pd
import time
from config import (
    PARQUET_DIR,
    YANDEX_CLOUD_API_KEY,
    YANDEX_CLOUD_FOLDER,
    YANDEX_CLOUD_MODEL,
)

client = openai.OpenAI(
  api_key=YANDEX_CLOUD_API_KEY,
  base_url="https://ai.api.cloud.yandex.net/v1",
  project=YANDEX_CLOUD_FOLDER
)

# user_request = 'ВВП России'
# code="40579"

def get_certain_data_from_file(user_request, code, verbose=True) -> str:
    file_path = PARQUET_DIR / f"{code}.parquet"
    # 1. Загружаем файл с реальными данными (CSV/Excel)
    df = pd.read_parquet(file_path)

    csv_path = Path("/tmp/temp_data.csv")
    df.to_csv(csv_path, index=False)

    # 2. Загружаем CSV файл (поддерживается)
    with open(csv_path, "rb") as f:
        uploaded_file = client.files.create(file=f, purpose="assistants")

    # 2. Создаем контейнер (песочницу) и кладем туда файл
    container = client.containers.create(
        name="data_analysis_task",
        expires_after={"anchor": "last_active_at", "minutes": 20},
        file_ids=[uploaded_file.id],
    )

    # time1 = time.perf_counter()

    df = pd.read_parquet(file_path)

    csv_path = Path("/tmp/temp_data.csv")
    df.to_csv(csv_path, index=False)

    # 2. Загружаем CSV файл (поддерживается)
    with open(csv_path, "rb") as f:
        uploaded_file = client.files.create(file=f, purpose="assistants")

    # print('TIMEEE ', time.perf_counter() - time1)
    # time2 = time.perf_counter()

    # 3. Запрос к модели с Code Interpreter
    response = client.responses.create(
        model=f"gpt://{YANDEX_CLOUD_FOLDER}/{YANDEX_CLOUD_MODEL}",
        input=f"""
        В контейнере находится файл .parquet. Он содержит экономические данные по странам.

        **Задача:**
        У нас есть данные в файле. Я показываю структуру (первые 2 строки для образца, которые считаны с помощью pandas - df.values.tolist()[:2]):
        {df.values.tolist()[:2]}

        Нужно выдать данные по запросу пользователя: {user_request}
        """,
        tools=[{"type": "code_interpreter", "container": container.id}],
        tool_choice={"type": "code_interpreter"},
    )

    # if verbose:
    #     for item in response.output:
    #         if item.type == "code_interpreter_call":
    #             print('-'*100)
    #             print(item.code)
    # if verbose:

    # if verbose:
    #     print("\n" + "="*60)
    #     print("📊 ИНФОРМАЦИЯ О ВЫПОЛНЕНИИ")
    #     print("="*60)
        
    #     # Перебираем все элементы ответа
    #     for item in response.output:
    #         # 1. Смотрим код, который написала модель
    #         if item.type == "code_interpreter_call":
    #             print("\n💻 СГЕНЕРИРОВАННЫЙ КОД:")
    #             print("-" * 40)
    #             print(item.code)
    #             print("-" * 40)
                
    #             # Если есть вывод из выполнения кода
    #             if hasattr(item, 'output') and item.output:
    #                 print("\n📤 ВЫВОД КОДА (stdout):")
    #                 print("-" * 40)
    #                 for output_item in item.output:
    #                     if output_item.type == "code_interpreter_output_text":
    #                         print(output_item.text)
    #                 print("-" * 40)
            
    #         # 2. Смотрим текстовый ответ модели (с пояснениями)
    #         if item.type == "message":
    #             print("\n💬 ОТВЕТ МОДЕЛИ:")
    #             print("-" * 40)
    #             for content in item.content:
    #                 if content.type == "output_text":
    #                     print(content.text)
    #             print("-" * 40)
            
    #         # 3. Скачиваем и сохраняем сгенерированные файлы (графики, csv и т.д.)
    #         if item.type == "message":
    #             for content in item.content:
    #                 if hasattr(content, "annotations"):
    #                     for ann in content.annotations:
    #                         if hasattr(ann, "file_id"):
    #                             # Скачиваем файл
    #                             filename = getattr(ann, 'filename', f"output_{ann.file_id}")
    #                             client.files.content(ann.file_id).write_to_file(filename)
    #                             print(f"\n📁 СОХРАНЕН ФАЙЛ: {filename}")
        
    #     print("\n" + "="*60)



    # print('TIMEEE ', time.perf_counter() - time2)

    # for item in response.output:
    #     if item.type == "message":
    #         for content in item.content:
    #             if hasattr(content, "annotations"):
    #                 for ann in content.annotations:
    #                     if hasattr(ann, "file_id"):
    #                         # Скачиваем файл (result.png)
    #                         client.files.content(ann.file_id).write_to_file(ann.filename)
    #                         print(f"Сохранен: {ann.filename}")


    return response.output_text

# print(get_certain_data_from_file('Покажи динамику инфляции в России (индекс потребительских цен) за 2014–2024 годы, годовые значения.', 33568))
# 33568
# 55396