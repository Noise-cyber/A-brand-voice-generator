"""Prompt templates for AI Brand Voice Generator (Gemini)."""
from __future__ import annotations

import json
from typing import Any, Dict, List


# --------- Brand Voice Analysis ---------
ANALYSIS_SYSTEM = (
    "You are a hybrid Brand Strategist, Linguistic Analyst, and senior Marketing "
    "Copywriter. Your task is to infer the *underlying* communication style behind "
    "a brand's writing samples. You do NOT repeat the samples back. You identify "
    "patterns: tone, rhythm, personality, vocabulary choices, and how the brand "
    "makes readers feel. You return ONLY valid JSON matching the requested schema."
)


def build_analysis_prompt(
    samples: str,
    brand_name: str = "",
    industry: str = "",
    audience: str = "",
    description: str = "",
) -> str:
    schema_example: Dict[str, Any] = {
        "overall_tone": "e.g. 'Warm, upbeat, and confidently casual'",
        "personality": ["3-6 short adjectives, e.g. 'friendly', 'witty'"],
        "formality": "One of: Very casual / Casual / Neutral / Professional / Formal",
        "emotional_style": "How the brand makes readers feel (1-2 sentences)",
        "vocabulary_style": "Describe word choices: simple, technical, poetic, punchy...",
        "sentence_style": "Short & punchy / Medium balanced / Long & flowing",
        "writing_rhythm": "Describe cadence: staccato, conversational, rhythmic, measured...",
        "humor_level": "None / Subtle / Moderate / Playful / Heavy",
        "confidence_level": "Understated / Balanced / Confident / Bold",
        "persuasiveness": "Soft / Balanced / Direct / Aggressive",
        "energy_level": "Calm / Steady / Energetic / High-energy",
        "emoji_usage": "None / Rare / Occasional / Frequent",
        "cta_style": "Describe how the brand asks readers to act (1 sentence)",
        "target_audience": "Who this voice is speaking to",
        "preferred_words": ["5-12 words the brand favors"],
        "preferred_phrases": ["3-8 signature phrase patterns"],
        "avoid_words": ["4-10 words that would feel off-brand"],
        "brand_characteristics": [
            "4-8 distinctive communication traits, e.g. 'ends with playful CTAs'"
        ],
        "writing_strengths": ["3-5 things this voice does well"],
    }

    context_lines: List[str] = []
    if brand_name:
        context_lines.append(f"Brand name: {brand_name}")
    if industry:
        context_lines.append(f"Industry: {industry}")
    if audience:
        context_lines.append(f"Target audience: {audience}")
    if description:
        context_lines.append(f"Brand description: {description}")
    context_block = "\n".join(context_lines) if context_lines else "(no extra context provided)"

    return f"""{ANALYSIS_SYSTEM}

# BRAND CONTEXT
{context_block}

# WRITING SAMPLES
Analyze the following raw samples. Do NOT copy sentences. Infer the underlying voice.

--- START SAMPLES ---
{samples}
--- END SAMPLES ---

# TASK
Return a single JSON object matching this exact schema (keys and types).
All fields must be filled with concrete, specific observations. Never say "N/A".

SCHEMA (example values shown for guidance only):
{json.dumps(schema_example, indent=2)}

Respond with the JSON object ONLY. No prose, no markdown fences.
"""


# --------- Content Generation ---------
GENERATION_SYSTEM = (
    "You are a professional marketing copywriter operating strictly inside a "
    "provided Brand Voice Profile. Every sentence you write must feel like it "
    "came from THIS brand. You never paste sample sentences. You never sound "
    "like a generic AI. You adapt the voice to the target platform while keeping "
    "the brand personality intact."
)


def build_generation_prompt(
    profile: Dict[str, Any],
    content_type: str,
    topic: str,
    goal: str,
    audience: str,
    extra_instructions: str,
    length: str,
    creativity: float,
    variations: int,
) -> str:
    length_guidance = {
        "Short": "Keep it tight. 1-3 short sentences or 20-50 words.",
        "Medium": "A balanced piece. 60-140 words. Multiple sentences, natural flow.",
        "Long": "A full piece. 180-320 words. Rich, structured, still on-brand.",
    }[length]

    return f"""{GENERATION_SYSTEM}

# BRAND VOICE PROFILE (must be followed strictly)
{json.dumps(profile, indent=2)}

# GENERATION REQUEST
- Content type: {content_type}
- Topic / Product: {topic}
- Marketing goal: {goal}
- Target audience: {audience or profile.get('target_audience', 'general')}
- Additional instructions: {extra_instructions or '(none)'}
- Length: {length} — {length_guidance}
- Creativity level (0=safe, 1=bold): {creativity:.2f}
- Number of variations to produce: {variations}

# HARD RULES
1. Match the overall_tone, personality, formality, vocabulary_style, sentence_style, and energy_level from the profile.
2. Prefer the words/phrases in preferred_words / preferred_phrases. Avoid the words in avoid_words.
3. Follow the emoji_usage guidance exactly.
4. Adapt to the "{content_type}" format (length, structure, platform conventions).
5. Respect the marketing goal — every variation should push toward "{goal}".
6. NEVER copy sentences from the original samples. Produce fresh, original writing.
7. Avoid generic AI clichés ("In today's fast-paced world", "Unlock the power of", "Elevate your", "game-changer", "revolutionize").
8. Keep the brand personality consistent across all {variations} variation(s).
9. Vary hooks, angles, and openings between variations — do not repeat structure.
10. Do not add explanations, headings, or commentary. Output ONLY the variations.

# OUTPUT FORMAT (strict)
Return exactly {variations} variation(s), each separated by a line containing only three hyphens.
Do NOT include labels like "Variation 1". Do NOT wrap in code fences.

Example separator between variations:
---

Produce the content now.
"""


# --------- Content Refinement ---------
REFINEMENT_SYSTEM = (
    "You are a senior editor. Your job is to refine existing marketing copy "
    "while preserving the brand voice defined in the profile. You apply the "
    "requested changes precisely, keep the core message and product facts, "
    "and never invent unrelated content."
)


def build_refinement_prompt(
    profile: Dict[str, Any],
    current_content: str,
    refinement_actions: List[str],
    custom_feedback: str,
    content_type: str,
    goal: str,
) -> str:
    actions_block = ", ".join(refinement_actions) if refinement_actions else "(none selected)"
    return f"""{REFINEMENT_SYSTEM}

# BRAND VOICE PROFILE (preserve this)
{json.dumps(profile, indent=2)}

# ORIGINAL CONTEXT
- Content type: {content_type}
- Marketing goal: {goal}

# CURRENT CONTENT (edit this, do not replace with unrelated writing)
\"\"\"
{current_content}
\"\"\"

# REQUESTED CHANGES
- Quick actions: {actions_block}
- Custom feedback: {custom_feedback or '(none)'}

# HARD RULES
1. Preserve the original message, product facts, offers, and any specific details.
2. Preserve the brand voice defined in the profile.
3. Apply the requested changes precisely — do not go beyond them.
4. Do not add commentary, headings, or explanations.
5. Return ONLY the refined content as plain text.
"""
