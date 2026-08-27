"""Gemini API service layer for the AI Brand Voice Generator."""
from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional, Tuple

from google import genai
from google.genai import types as genai_types

from config import GEMINI_API_KEY, GEMINI_MODEL
from prompts import (
    build_analysis_prompt,
    build_generation_prompt,
    build_refinement_prompt,
)


class GeminiServiceError(Exception):
    """Wraps failures from the Gemini API layer."""


# ---------- Client ----------
_CLIENT: Optional[genai.Client] = None


def initialize_gemini(api_key: Optional[str] = None) -> genai.Client:
    """Return a cached Gemini client. Raises if no API key is available."""
    global _CLIENT
    key = (api_key or GEMINI_API_KEY or "").strip()
    if not key:
        raise GeminiServiceError(
            "Gemini API key is missing. Set GEMINI_API_KEY in your environment or .env file."
        )
    if _CLIENT is None:
        try:
            _CLIENT = genai.Client(api_key=key)
        except Exception as exc:  # pragma: no cover
            raise GeminiServiceError(f"Failed to initialize Gemini client: {exc}") from exc
    return _CLIENT


def _generate(
    prompt: str,
    temperature: float = 0.7,
    response_mime_type: Optional[str] = None,
    model: Optional[str] = None,
) -> str:
    client = initialize_gemini()
    try:
        config = genai_types.GenerateContentConfig(
            temperature=temperature,
            response_mime_type=response_mime_type or "text/plain",
        )
        response = client.models.generate_content(
            model=model or GEMINI_MODEL,
            contents=prompt,
            config=config,
        )
    except Exception as exc:
        raise GeminiServiceError(f"Gemini API request failed: {exc}") from exc

    text = getattr(response, "text", None)
    if not text or not text.strip():
        raise GeminiServiceError("Gemini returned an empty response.")
    return text.strip()


# ---------- Validation ----------
def validate_brand_samples(samples: str, min_chars: int = 80) -> Tuple[bool, str]:
    if not samples or not samples.strip():
        return False, "Please paste at least one sample of your brand's writing."
    if len(samples.strip()) < min_chars:
        return (
            False,
            f"Please provide at least {min_chars} characters of sample content "
            "(more samples = a sharper voice profile).",
        )
    return True, ""


def validate_generation_input(topic: str) -> Tuple[bool, str]:
    if not topic or not topic.strip():
        return False, "Please enter a topic or product to generate content about."
    return True, ""


# ---------- Response parsing ----------
def parse_brand_voice_response(raw: str) -> Dict[str, Any]:
    """Extract the JSON object from a Gemini analysis response."""
    if not raw:
        raise GeminiServiceError("Empty analysis response from Gemini.")

    # Strip common markdown fences
    cleaned = raw.strip()
    fence = re.match(r"^```(?:json)?\s*(.*?)\s*```$", cleaned, re.DOTALL)
    if fence:
        cleaned = fence.group(1).strip()

    # Try direct parse first
    try:
        return _normalize_profile(json.loads(cleaned))
    except json.JSONDecodeError:
        pass

    # Fallback: grab first {...} block
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if match:
        try:
            return _normalize_profile(json.loads(match.group(0)))
        except json.JSONDecodeError as exc:
            raise GeminiServiceError(f"Could not parse Gemini JSON: {exc}") from exc

    raise GeminiServiceError("Gemini did not return a valid JSON profile.")


_LIST_FIELDS = {
    "personality",
    "preferred_words",
    "preferred_phrases",
    "avoid_words",
    "brand_characteristics",
    "writing_strengths",
}
_STRING_FIELDS = {
    "overall_tone",
    "formality",
    "emotional_style",
    "vocabulary_style",
    "sentence_style",
    "writing_rhythm",
    "humor_level",
    "confidence_level",
    "persuasiveness",
    "energy_level",
    "emoji_usage",
    "cta_style",
    "target_audience",
}


def _normalize_profile(profile: Dict[str, Any]) -> Dict[str, Any]:
    """Guarantee expected keys/types so the UI never explodes."""
    if not isinstance(profile, dict):
        raise GeminiServiceError("Analysis response was not a JSON object.")

    normalized: Dict[str, Any] = {}
    for key in _STRING_FIELDS:
        val = profile.get(key, "")
        normalized[key] = str(val).strip() if val is not None else ""
    for key in _LIST_FIELDS:
        val = profile.get(key, [])
        if isinstance(val, str):
            val = [v.strip() for v in val.split(",") if v.strip()]
        if not isinstance(val, list):
            val = []
        normalized[key] = [str(v).strip() for v in val if str(v).strip()]
    return normalized


def _split_variations(raw: str, expected: int) -> List[str]:
    """Split Gemini output into individual variations."""
    if not raw:
        return []
    # Remove code fences if present
    cleaned = re.sub(r"^```[a-zA-Z]*\s*|\s*```$", "", raw.strip(), flags=re.MULTILINE)
    # Split on lines that are just --- (allow whitespace)
    parts = re.split(r"(?m)^\s*-{3,}\s*$", cleaned)
    parts = [p.strip() for p in parts if p.strip()]
    # Strip labels like "Variation 1:" or "1." at the start
    stripped: List[str] = []
    for p in parts:
        p = re.sub(r"^(?:Variation\s*\d+[:\.\)]?|\*\*Variation\s*\d+\*\*|\d+[\.\)])\s*",
                   "", p, flags=re.IGNORECASE).strip()
        stripped.append(p)
    if not stripped:
        stripped = [cleaned.strip()]
    # If we got fewer than expected, that's fine — return what we have
    return stripped[:expected] if len(stripped) >= expected else stripped


# ---------- Public API ----------
def analyze_brand_voice(
    samples: str,
    brand_name: str = "",
    industry: str = "",
    audience: str = "",
    description: str = "",
) -> Dict[str, Any]:
    prompt = build_analysis_prompt(samples, brand_name, industry, audience, description)
    raw = _generate(prompt, temperature=0.35, response_mime_type="application/json")
    return parse_brand_voice_response(raw)


def generate_content(
    profile: Dict[str, Any],
    content_type: str,
    topic: str,
    goal: str,
    audience: str,
    extra_instructions: str,
    length: str,
    creativity: float,
    variations: int,
) -> List[str]:
    prompt = build_generation_prompt(
        profile=profile,
        content_type=content_type,
        topic=topic,
        goal=goal,
        audience=audience,
        extra_instructions=extra_instructions,
        length=length,
        creativity=creativity,
        variations=variations,
    )
    # Map creativity slider to sensible temperature range
    temperature = max(0.1, min(1.2, 0.2 + creativity * 1.0))
    raw = _generate(prompt, temperature=temperature)
    parts = _split_variations(raw, variations)
    if not parts:
        raise GeminiServiceError("Gemini did not return any usable content.")
    return parts


def refine_content(
    profile: Dict[str, Any],
    current_content: str,
    refinement_actions: List[str],
    custom_feedback: str,
    content_type: str,
    goal: str,
) -> str:
    if not current_content or not current_content.strip():
        raise GeminiServiceError("Nothing to refine — the content is empty.")
    if not refinement_actions and not (custom_feedback and custom_feedback.strip()):
        raise GeminiServiceError(
            "Choose at least one quick action or enter custom feedback to refine."
        )
    prompt = build_refinement_prompt(
        profile=profile,
        current_content=current_content,
        refinement_actions=refinement_actions,
        custom_feedback=custom_feedback,
        content_type=content_type,
        goal=goal,
    )
    return _generate(prompt, temperature=0.55).strip()
