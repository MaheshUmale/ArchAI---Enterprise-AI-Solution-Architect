from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from app.core.config import settings

def get_llm(temperature=0.0, model=None):
    """
    Returns an LLM instance based on available environment variables.
    Priority: Local > Groq > SambaNova > Together > Gemini > Anthropic > OpenAI
    """
    if model is None:
        # Check for local model first if enabled/specified via env
        if os.getenv("USE_LOCAL_LLM") == "true":
            model = os.getenv("LOCAL_MODEL_NAME", "phi3.5")
            return ChatOpenAI(
                model=model,
                temperature=temperature,
                api_key="local-placeholder",
                base_url=settings.LOCAL_LLM_URL
            )

        if settings.GROQ_API_KEY:
            model = "llama-3.3-70b-versatile"
        elif settings.SAMBANOVA_API_KEY:
            model = "Meta-Llama-3.1-405B-Instruct"
        elif settings.TOGETHER_API_KEY:
            model = "meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo"
        elif settings.GOOGLE_API_KEY:
            model = "gemini-2.0-flash"
        elif settings.ANTHROPIC_API_KEY or settings.CLAUDE_API_KEY:
            model = "claude-3-5-sonnet-20240620"
        elif settings.OPENAI_API_KEY:
            model = "gpt-4o"
        else:
            raise ValueError("No LLM API keys found in environment")

    if "llama" in model.lower() or "mixtral" in model.lower() or "gemma" in model.lower():
        # Check if it's SambaNova or Together via API key availability if model name is ambiguous
        # but usually we can check provider-specific prefix or use model name.
        if settings.SAMBANOVA_API_KEY and ("Samba" in model or model.startswith("Meta-Llama-3.1-405B")):
             return ChatOpenAI(
                model=model,
                temperature=temperature,
                api_key=settings.SAMBANOVA_API_KEY,
                base_url="https://api.sambanova.ai/v1"
            )
        elif settings.TOGETHER_API_KEY and ("together" in model.lower() or "meta-llama/Meta-Llama-3.1-405B" in model):
            return ChatOpenAI(
                model=model,
                temperature=temperature,
                api_key=settings.TOGETHER_API_KEY,
                base_url="https://api.together.xyz/v1"
            )

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
