# AI Brand Voice Generator

Teach AI how your brand speaks — then generate on-brand marketing content in seconds.

Built with **Streamlit + Python + Google Gemini**.

## Workflow

**Sample Content → Brand Voice Analysis → Brand Voice Profile → Content Generation → Refinement**

---

## Features

- **Voice Analysis** — Analyze existing brand writing and extract a structured Brand Voice Profile.
- **Tone Analysis** — Identify tone, personality, formality, emotional style, vocabulary, sentence style, rhythm, humor, confidence, energy, emoji usage, and CTA style.
- **Vocabulary Guardrails** — Identify preferred words, preferred phrases, and words to avoid.
- **Brand Characteristics** — Extract distinctive communication traits and writing strengths.
- **11 Content Formats**
  - Instagram Post
  - LinkedIn Post
  - X/Twitter Post
  - Marketing Email
  - Product Description
  - Advertisement Copy
  - Ad Headline
  - Tagline
  - Blog Introduction
  - Product Announcement
  - Website Copy
- **Multi-variation Generation** — Generate up to 5 variations.
- **Creativity Control** — Adjust how conservative or creative the generated content should be.
- **Content Refinement** — Improve generated content using quick actions or custom feedback.
- **Copy to Clipboard** — Copy generated variations directly from the interface.
- **Session-Based Profile** — The analyzed brand voice stays available during the current Streamlit session.
- **Demo Samples** — Includes Lifestyle/Fashion and B2B Technology examples.

---

## Tech Stack

| Layer | Technology |
|---|---|
| UI | Streamlit |
| Backend | Python |
| AI | Google Gemini |
| Gemini SDK | `google-genai` |
| Configuration | `python-dotenv` |
| Model | `gemini-3.5-flash` |

---

## Project Structure

```text
ai-brand-voice-generator/
│
├── app.py
├── gemini_service.py
├── prompts.py
├── config.py
├── utils.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
│
└── .streamlit/
    └── config.toml
