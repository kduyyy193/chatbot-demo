from openai import OpenAI
from src.config.settings import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)
response = client.chat.completions.create(
    model="gpt-4o-mini-2024-07-18",
    messages=[{"role": "user", "content": "Hello"}]
)
print(response.choices[0].message.content)
