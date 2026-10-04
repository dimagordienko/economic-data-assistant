import openai
from config import YANDEX_CLOUD_API_KEY, YANDEX_CLOUD_FOLDER, YANDEX_CLOUD_MODEL

client = openai.OpenAI(
  api_key=YANDEX_CLOUD_API_KEY,
  base_url="https://ai.api.cloud.yandex.net/v1",
  project=YANDEX_CLOUD_FOLDER
)

def get_final_llm_answer(user_request, data) -> str:
    response = client.responses.create(
        model=f"gpt://{YANDEX_CLOUD_FOLDER}/{YANDEX_CLOUD_MODEL}",
        input=f"""
        === ДАННЫЕ ===
        {data}
        
        === ЗАПРОС ===
        {user_request}
        
        === ИНСТРУКЦИЯ ===
        Ответь на запрос точно по данным, не добавляй информацию из своих знаний.
        """
    )

    return response.output_text