"""Configuration for AI Brand Voice Generator."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import List

from dotenv import load_dotenv

load_dotenv()


# ---------- Model / API ----------

GEMINI_API_KEY: str = os.environ.get("GEMINI_API_KEY", "").strip()

GEMINI_MODEL: str = os.environ.get(
    "GEMINI_MODEL",
    "gemini-3.5-flash",
).strip()


# ---------- Content Options ----------

CONTENT_TYPES: List[str] = [
    "Instagram Post",
    "LinkedIn Post",
    "X/Twitter Post",
    "Marketing Email",
    "Product Description",
    "Advertisement Copy",
    "Ad Headline",
    "Tagline",
    "Blog Introduction",
    "Product Announcement",
    "Website Copy",
]

MARKETING_GOALS: List[str] = [
    "Awareness",
    "Engagement",
    "Lead Generation",
    "Sales",
    "Product Launch",
    "Education",
    "Conversion",
    "Community Building",
]

CONTENT_LENGTHS: List[str] = [
    "Short",
    "Medium",
    "Long",
]

REFINEMENT_ACTIONS: List[str] = [
    "Make Shorter",
    "Make Longer",
    "More Professional",
    "More Casual",
    "More Persuasive",
    "More Emotional",
    "More Playful",
    "Stronger CTA",
    "Remove Emojis",
    "Add Emojis",
    "Simplify Language",
]


# ---------- Defaults ----------

@dataclass
class Defaults:
    creativity: float = 0.7
    length: str = "Medium"
    variations: int = 3
    min_sample_chars: int = 80


DEFAULTS = Defaults()


# ---------- Demo Samples ----------

@dataclass
class DemoSample:
    label: str
    brand_name: str
    industry: str
    audience: str
    description: str
    samples: str


DEMO_SAMPLES: List[DemoSample] = [
    DemoSample(
        label="Lifestyle / Fashion (Playful)",
        brand_name="Sundaze",
        industry="Lifestyle & Fashion",
        audience="Gen Z & millennial creatives who love sunny weekends",
        description=(
            "A joyful lifestyle brand making everyday moments feel "
            "like a mini-vacation."
        ),
        samples=(
            "Sunday mornings, but make it iced coffee and no alarms.\n\n"
            "Your closet called — it's begging for a color upgrade. We got you.\n\n"
            "Tiny wins today > perfect plans someday. "
            "Slip on the good vibes and go.\n\n"
            "New drop alert: linen sets that feel like a hug from the sun.\n\n"
            "You don't need a reason to feel good. But if you do, here's one: "
            "20% off, just for the weekend."
        ),
    ),
    DemoSample(
        label="B2B Technology (Professional)",
        brand_name="Northpoint Analytics",
        industry="B2B SaaS / Data Analytics",
        audience="Data leaders and RevOps teams at mid-market SaaS companies",
        description=(
            "Enterprise-grade analytics platform helping revenue teams "
            "close the reporting gap."
        ),
        samples=(
            "Revenue teams spend 40% of their week reconciling reports. "
            "Northpoint replaces that entire workflow in a single unified view.\n\n"
            "Introducing Model Sync — pipeline forecasts that update the moment "
            "your CRM does. No manual refresh. No stale numbers.\n\n"
            "Our latest benchmark study analyzed 220 mid-market SaaS companies. "
            "The finding: teams using unified analytics closed 27% faster on average.\n\n"
            "Enterprise-ready, SOC 2 Type II certified, and deployable in under "
            "a week. See what your data can actually do."
        ),
    ),
]
