from dataclasses import dataclass
import os
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Settings:
    OPENAI_API_KEY: str
    MODEL_NAME: str
    CREDITS_DEFAULT: int
    CREDITS_COST_PER_MSG: int
    PAYMENT_URL: str
    RATE_LIMIT_PER_MINUTE: int

def _load_settings() -> Settings:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY environment variable is required")
    return Settings(
        OPENAI_API_KEY=api_key,
        MODEL_NAME=os.getenv("MODEL_NAME", "gpt-4o-mini"),
        CREDITS_DEFAULT=int(os.getenv("CREDITS_DEFAULT", "100")),
        CREDITS_COST_PER_MSG=int(os.getenv("CREDITS_COST_PER_MSG", "1")),
        PAYMENT_URL=os.getenv("PAYMENT_URL", "https://mi-dominio.com/pagar"),
        RATE_LIMIT_PER_MINUTE=int(os.getenv("RATE_LIMIT_PER_MINUTE", "10")),
    )

settings = _load_settings()
