"""Small wrapper around the supported Google GenAI Python SDK."""

from google import genai
from google.genai import types


DEFAULT_GEMINI_MODEL = "gemini-3.8-flash"

RETIRED_GEMINI_MODELS = {
    "gemini-1.5-flash",
    "gemini-1.5-pro",
    "gemini-1.5-flash-8b",
    "gemini-1.5-flash-002",
    "gemini-1.5-pro-002",
    "gemini-2.0-flash",
    "gemini-2.0-flash-exp",
    "gemini-3-pro-preview",
}


def resolve_gemini_model(model: str = "auto") -> str:
    """Resolve automatic and retired model selections to a supported default."""
    if not model or model == "auto" or model in RETIRED_GEMINI_MODELS:
        return DEFAULT_GEMINI_MODEL
    return model


def get_gemini_model_info(api_key: str, model: str = "auto"):
    """Check API-key access to a model without generating billable content."""
    client = genai.Client(api_key=api_key)
    return client.models.get(model=resolve_gemini_model(model))


def generate_gemini_text(
    api_key: str,
    model: str,
    prompt: str,
    max_output_tokens: int = 1024,
) -> str:
    """Generate text through the current Google GenAI client."""
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=resolve_gemini_model(model),
        contents=prompt,
        config=types.GenerateContentConfig(
            max_output_tokens=max(1, int(max_output_tokens)),
        ),
    )
    text = response.text
    if not text or not text.strip():
        raise ValueError("Gemini returned an empty response")
    return text.strip()
