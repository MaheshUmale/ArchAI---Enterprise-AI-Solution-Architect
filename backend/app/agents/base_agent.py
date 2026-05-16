from langchain_openai import ChatOpenAI
from app.core.config import settings

def get_llm(temperature=0.0, model="gpt-4o"):
    return ChatOpenAI(
        model=model,
        temperature=temperature,
        api_key=settings.OPENAI_API_KEY
    )
