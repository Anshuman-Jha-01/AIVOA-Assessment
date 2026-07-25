"""
Thin wrapper around the Groq SDK.

Why wrap it instead of calling Groq directly from the agent nodes?
- One place to swap models (gemma2-9b-it primary, llama-3.3-70b-versatile fallback)
- One place to enforce "always return JSON" for structured-extraction calls
- One place to handle retries/errors so agent nodes stay readable
"""
import json
import logging

from groq import Groq

from app.core.config import settings

logger = logging.getLogger("aivoa.groq")

_client = Groq(api_key=settings.GROQ_API_KEY) if settings.GROQ_API_KEY else None


def _get_client() -> Groq:
    global _client
    if _client is None:
        _client = Groq(api_key=settings.GROQ_API_KEY)
    return _client


def chat_completion(
    system_prompt: str,
    user_prompt: str,
    json_mode: bool = False,
    model: str | None = None,
    temperature: float = 0.2,
) -> str:
    """Call Groq chat completion. Falls back to the larger model on failure/timeout."""
    client = _get_client()
    chosen_model = model or settings.GROQ_PRIMARY_MODEL

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    kwargs = {}
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}

    try:
        resp = client.chat.completions.create(
            model=chosen_model,
            messages=messages,
            temperature=temperature,
            **kwargs,
        )
        return resp.choices[0].message.content
    except Exception as e:
        logger.warning(f"Groq call failed on {chosen_model} ({e}); retrying with fallback model")
        resp = client.chat.completions.create(
            model=settings.GROQ_FALLBACK_MODEL,
            messages=messages,
            temperature=temperature,
            **kwargs,
        )
        return resp.choices[0].message.content


def chat_completion_json(system_prompt: str, user_prompt: str, model: str | None = None) -> dict:
    """Call Groq and parse the response as JSON, with a defensive fallback if the
    model wraps the JSON in markdown fences or adds stray text."""
    raw = chat_completion(system_prompt, user_prompt, json_mode=True, model=model)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        cleaned = raw.strip().strip("`")
        if cleaned.startswith("json"):
            cleaned = cleaned[4:]
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start != -1 and end != -1:
            return json.loads(cleaned[start:end + 1])
        raise
