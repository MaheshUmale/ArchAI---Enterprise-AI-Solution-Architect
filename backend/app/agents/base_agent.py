from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from app.core.config import settings

def get_llm(temperature=0.0, model=None):
    """
    Returns an LLM instance based on available environment variables.
    Priority: Groq > Gemini > Anthropic > OpenAI
    """
    if model is None:
        if settings.GROQ_API_KEY:
            model = "llama-3.3-70b-versatile"
        elif settings.GOOGLE_API_KEY:
            model = "gemini-2.0-flash"
        elif settings.ANTHROPIC_API_KEY or settings.CLAUDE_API_KEY:
            model = "claude-3-5-sonnet-20240620"
        elif settings.OPENAI_API_KEY:
            model = "gpt-4o"
        else:
            raise ValueError("No LLM API keys found in environment")

    if "llama" in model.lower() or "mixtral" in model.lower() or "gemma" in model.lower():
        return ChatGroq(
            model=model,
            temperature=temperature,
            groq_api_key=settings.GROQ_API_KEY
        )
    elif "gemini" in model.lower():
        return ChatGoogleGenerativeAI(
            model=model,
            temperature=temperature,
            google_api_key=settings.GOOGLE_API_KEY
        )
    elif "gpt" in model.lower():
        return ChatOpenAI(
            model=model,
            temperature=temperature,
            api_key=settings.OPENAI_API_KEY
        )
    elif "claude" in model.lower():
        api_key = settings.ANTHROPIC_API_KEY or settings.CLAUDE_API_KEY
        return ChatAnthropic(
            model=model,
            temperature=temperature,
            anthropic_api_key=api_key
        )

    raise ValueError(f"Unsupported model: {model}")
