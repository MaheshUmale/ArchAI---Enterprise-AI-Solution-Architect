from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from app.core.config import settings

def get_llm(temperature=0.0, model=None):
    """
    Returns an LLM instance based on available environment variables.
    Defaults to gpt-4o if OPENAI_API_KEY is present,
    otherwise falls back to claude-3-5-sonnet-20240620 if ANTHROPIC_API_KEY is present.
    """
    if model is None:
        if settings.ANTHROPIC_API_KEY or settings.CLAUDE_API_KEY:
            model = "claude-3-5-sonnet-20240620"
        elif settings.OPENAI_API_KEY:
            model = "gpt-4o"
        else:
            raise ValueError("No LLM API keys found in environment (OPENAI_API_KEY or ANTHROPIC_API_KEY)")

    if "gpt" in model.lower():
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
