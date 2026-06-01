import os
from pathlib import Path
from typing import Dict, Optional

from src.core.llm_provider import LLMProvider


def create_provider_from_env(
    provider: Optional[str] = None,
    model: Optional[str] = None,
) -> LLMProvider:
    """
    Create a provider from explicit args or .env defaults.
    """
    config = _load_config()

    provider_name = (provider or config.get("DEFAULT_PROVIDER", "openai")).lower()
    model_name = model or config.get("DEFAULT_MODEL")

    if provider_name == "openai":
        from src.core.openai_provider import OpenAIProvider

        return OpenAIProvider(
            model_name=_first_model(model_name or config.get("model") or "gpt-4o"),
            api_key=(
                config.get("OPENAI_API_KEY")
                or config.get("api_key")
                or config.get("api_key1")
                or config.get("api_key2")
            ),
            base_url=_normalize_base_url(
                config.get("OPENAI_BASE_URL") or config.get("BASE_URL") or config.get("host")
            ),
        )

    if provider_name in {"google", "gemini"}:
        from src.core.gemini_provider import GeminiProvider

        return GeminiProvider(
            model_name=model_name or "gemini-1.5-flash",
            api_key=config.get("GEMINI_API_KEY") or config.get("api_key2"),
        )

    raise ValueError(
        f"Unsupported provider '{provider_name}'. Use one of: openai, google."
    )


def _load_config(env_path: str = ".env") -> Dict[str, str]:
    """
    Load standard KEY=value files plus the lab's loose "key: value" format.
    Environment variables win over file values.
    """
    config = dict(os.environ)
    path = Path(env_path)
    if not path.exists():
        return config

    for raw_line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        separator = "=" if "=" in line else ":" if ":" in line else None
        if not separator:
            continue

        key, value = line.split(separator, 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and value and key not in config:
            config[key] = value
            config[key.upper()] = value

    return config


def _first_model(model_value: str) -> str:
    """
    Support lab env values like "xmtp/mimo-v2.5, xmtp/mimo-v2.5-pro".
    """
    return model_value.split(",", 1)[0].strip()


def _normalize_base_url(base_url: Optional[str]) -> str:
    """
    Prefer the required lab gateway and handle loose notes like
    "http://localhost:20128/v1 or https://...".
    """
    if not base_url:
        return "http://localhost:20128/v1"

    value = base_url.strip()
    if "localhost:20128" in value:
        start = value.find("http://localhost:20128")
        value = value[start:].split()[0]
    elif " or " in value:
        value = value.split(" or ", 1)[0].strip()

    return value.rstrip("/")
