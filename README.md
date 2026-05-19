# ИИ Ассистент для экономистов
## hack_mai

Проект для ответа на аналитические вопросы:
- сначала ищется наиболее подходящий показатель в локальной векторной базе (`DuckDB + embeddings`);
- затем из соответствующего `.parquet` файла извлекаются нужные значения через `Code Interpreter`;
- при нехватке данных выполняются дополнительные итерации поиска;
- после этого LLM формирует финальный ответ только на основе найденных данных.

## Что лежит в проекте

- `main.py` — основной сценарий пайплайна (запрос -> поиск -> добор данных -> финальный ответ).
- `create_json.py` — преобразует пользовательский запрос в структурированный JSON (тип поиска, ключевые слова, фильтры).
- `search_top_k.py` — векторный поиск по таблице `fedstatru` в `my_db.duckdb`.
- `find_data_with_code.py` — получает `code` показателя и запускает извлечение конкретных данных.
- `connect_to_code_interpretator.py` — загружает нужный `.parquet` в контейнер и просит LLM/Code Interpreter извлечь данные под вопрос.
- `ask_llm_for_data.py` — проверяет, хватает ли собранных данных, и генерирует короткий поисковый запрос для следующей итерации.
- `final_llm_annswer.py` — формирует итоговый ответ по собранному набору данных.
- `load_to_duckDB.py` — одноразовая сборка локальной базы эмбеддингов (`knowledge_base_fedstatru_real.csv` -> `my_db.duckdb`).
- `knowledge_base_fedstatru_real.csv` — база метаданных/описаний показателей для векторного поиска.
- `my_db.duckdb` — готовая локальная БД с таблицей `fedstatru` и колонкой `embedding`.
- `clean_dataset.py` — вспомогательный/черновой скрипт для подготовки данных (сейчас не участвует в основном пайплайне).

## Как это работает (пошагово)

1. Пользовательский запрос передается в `create_json.py`, где LLM определяет:
   - `search_type` (`keyword` / `vector` / `hybrid`),
   - `semantic_query`,
   - `keyword_query`,
   - `filters`.
2. `search_top_k.py` по `semantic_query` делает cosine similarity по эмбеддингам в DuckDB и возвращает лучший показатель (его `code` и метаинформацию).
3. `find_data_with_code.py` и `connect_to_code_interpretator.py` открывают соответствующий `parquet` по `code`, загружают его в контейнер и извлекают конкретные цифры под вопрос.
4. `ask_llm_for_data.py` решает, достаточно ли найденных данных. Если нет — выдает короткий поисковый запрос, и шаги 2-3 повторяются (до 3 итераций в `main.py`).
5. `final_llm_annswer.py` формирует итоговый текстовый ответ, опираясь только на собранные данные.

## Быстрый запуск

### 1) Установить зависимости

Linux/macOS:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Windows (PowerShell):

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2) Настроить переменные окружения

```bash
cp .env.example .env
```

Заполните `.env`:
- `YANDEX_CLOUD_FOLDER`
- `YANDEX_CLOUD_API_KEY`
- `YANDEX_CLOUD_MODEL`

### 3) Подготовить данные

Обязательно положите parquet-файлы Fedstat в папку:
- `dumps/fedstatru/fedstatru/data/parquet/`

Должна быть папка dumps в иэрархии, которую предоставляли в качестве данных


По умолчанию в проекте уже есть:
- `knowledge_base_fedstatru_real.csv`
- `my_db.duckdb`

Если хотите пересобрать `my_db.duckdb` из CSV:

```bash
python load_to_duckDB.py
```

### 4) Выполнить запрос

Открыть `main.py`:

```bash
python main.py
```

## Важные пути и предпосылки

Проект использует относительные пути от корня репозитория:
- `knowledge_base_fedstatru_real.csv`
- `my_db.duckdb`
- `dumps/fedstatru/fedstatru/data/parquet/`

Поэтому код работает в любой папке/на любой машине при сохранении этой структуры.

## Технические ограничения текущей версии

- Поиск сейчас фактически идет через `semantic_query` и `top_k=1` (без ранжирования нескольких кандидатов).
- Есть лимит повторных попыток добора данных (`n == 3`), который можно увеличить(каждый запрос API Yandex обрабатывает 30-60 секунд).
- Ключи/API-параметры читаются из `.env`.

## Минимальная схема потока

`main.py`  
-> `create_json.py`  
-> `search_top_k.py`  
-> `find_data_with_code.py`  
-> `connect_to_code_interpretator.py`  
-> `ask_llm_for_data.py` (цикл при нехватке данных)  
-> `final_llm_annswer.py`


При всех вопросах просьба обращаться в телеграм: @BuyMeKoenigsegg
