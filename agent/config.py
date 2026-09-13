from __future__ import annotations

import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic import BaseModel

# Load environment variables from .env file explicitly
ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=ENV_PATH)


class Settings(BaseModel):
    project_name: str = "GeM Compliance Agent"
    default_model: str = os.getenv("DEFAULT_MODEL", "openai/gpt-4o-mini")
    openrouter_api_key: str | None = os.getenv("OPENROUTER_API_KEY")
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
    openrouter_base_url: str = "https://openrouter.ai/api/v1"

    @property
    def active_api_key(self) -> str | None:
        return self.openrouter_api_key or self.openai_api_key


settings = Settings()