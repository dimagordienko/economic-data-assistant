import duckdb
from sentence_transformers import SentenceTransformer
from config import DB_PATH

TABLE_NAME = "fedstatru"

model = SentenceTransformer("intfloat/multilingual-e5-base")
con = duckdb.connect(DB_PATH)


def search(query: str, top_k: int = 1):
    query_embedding = model.encode(
        [f"query: {query}"],
        normalize_embeddings=True
    )[0].tolist()

    embedding_str = "[" + ",".join(map(str, query_embedding)) + "]"

    query_sql = f"""
        SELECT *,
               array_cosine_similarity(
                   embedding::DOUBLE[768],
                   {embedding_str}::DOUBLE[768]
               ) AS score
        FROM {TABLE_NAME}
        ORDER BY score DESC
        LIMIT {top_k}
    """
    in_df = con.execute(query_sql).df()
    return in_df[['code', 'name', 'url', 'Единицы измерения',
       'Периодичность и характеристика временного ряда', 'Период действия',
       'Длина временного ряда', 'Последнее обновление данных',
       'Признаки (перечень на базе классификаторов и справочников)',
       'Методологические пояснения',
       'Источники и способ формирования показателя',
       'Ведомство (субъект статистического учета)', 'Подразделение',
       'Размещение', 'Комментарий']].values.tolist()


# result = search("ВВП России", top_k=1)

# print(result)