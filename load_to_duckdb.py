import pandas as pd
import duckdb
from sentence_transformers import SentenceTransformer
from config import CSV_PATH, DB_PATH

TEXT_COLUMN = "text"   # колонка, которую эмбеддим
TABLE_NAME = "fedstatru"

# 1. читаем csv
df = pd.read_csv(CSV_PATH)

# 2. модель
model = SentenceTransformer("intfloat/multilingual-e5-base")

texts = [f"passage: {text}" for text in df[TEXT_COLUMN].astype(str)]

embeddings = model.encode(
    texts,
    batch_size=32,
    show_progress_bar=True,
    normalize_embeddings=True
)

# новая колонка
df["embedding"] = embeddings.tolist()

print(df.columns)
print(df.head())

# 3. подключаем duckdb
con = duckdb.connect(DB_PATH)

# DuckDB сам создаст схему на основе dataframe
con.register("temp_df", df)

con.execute(f"""
    CREATE OR REPLACE TABLE {TABLE_NAME} AS
    SELECT * FROM temp_df
""")

print("Все колонки загружены")