"""UI helpers for AI Brand Voice Generator."""
from __future__ import annotations

import html
import json
from typing import Any, Dict, List

import streamlit as st


# ---------- Session helpers ----------
def init_session_state() -> None:
    ss = st.session_state
    ss.setdefault("brand_profile", None)
    ss.setdefault(
        "brand_meta",
        {
            "brand_name": "",
            "industry": "",
            "audience": "",
            "description": "",
        },
    )
    ss.setdefault("samples", "")
    ss.setdefault("generated_variations", [])
    ss.setdefault("generation_meta", None)
    ss.setdefault("copied_index", None)
    ss.setdefault("refining_index", None)
    ss.setdefault("last_error", None)


def reset_session() -> None:
    keys = [
        "brand_profile",
        "samples",
        "generated_variations",
        "generation_meta",
        "copied_index",
        "refining_index",
        "last_error",
    ]

    for k in keys:
        st.session_state[k] = (
            None
            if k
            in {
                "brand_profile",
                "generation_meta",
                "copied_index",
                "refining_index",
                "last_error",
            }
            else ([] if k == "generated_variations" else "")
        )

    st.session_state["brand_meta"] = {
        "brand_name": "",
        "industry": "",
        "audience": "",
        "description": "",
    }


# ---------- CSS ----------
def load_css() -> None:
    st.markdown(
        """
        <style>
        @import url('https://api.fontshare.com/v2/css?f[]=cabinet-grotesk@500,700,800&f[]=general-sans@400,500,600&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&display=swap');

        :root {
          --bg: #F4F1EA;
          --sidebar-bg: #EBE8E0;
          --surface: #FFFFFF;
          --text-main: #111111;
          --text-secondary: #555555;
          --text-tertiary: #888888;
          --brand: #FF331F;
          --brand-hover: #E62E1C;
          --border: #D1CDC5;
        }

        .stApp {
          background-color: var(--bg);
          color: var(--text-main);
          font-family: 'General Sans', sans-serif;
        }

        [data-testid="stSidebar"] {
          background-color: var(--sidebar-bg);
          border-right: 1px solid var(--border);
        }

        [data-testid="stSidebar"] .stMarkdown,
        [data-testid="stSidebar"] label {
          color: var(--text-main);
        }

        h1, h2, h3, h4 {
          font-family: 'Cabinet Grotesk', sans-serif !important;
          color: var(--text-main);
          letter-spacing: -0.02em;
          font-weight: 800;
        }

        h1 {
          font-size: 2.6rem;
          line-height: 1.05;
        }

        h2 {
          font-size: 1.6rem;
          margin-top: 0.5rem;
        }

        h3 {
          font-size: 1.15rem;
          text-transform: uppercase;
          letter-spacing: 0.04em;
        }

        .e1-hero {
          border: 1px solid var(--text-main);
          background: var(--surface);
          padding: 2rem 2rem 1.75rem;
          box-shadow: 6px 6px 0 0 var(--brand);
          margin-bottom: 2rem;
        }

        .e1-hero .eyebrow {
          font-family: 'IBM Plex Mono', monospace;
          font-size: 0.75rem;
          text-transform: uppercase;
          letter-spacing: 0.14em;
          color: var(--brand);
          margin-bottom: 0.75rem;
        }

        .e1-hero h1 {
          margin: 0 0 0.75rem 0;
        }

        .e1-hero .subtitle {
          font-size: 1.15rem;
          color: var(--text-main);
          font-weight: 500;
          margin-bottom: 0.5rem;
        }

        .e1-hero .desc {
          color: var(--text-secondary);
          max-width: 720px;
          font-size: 0.98rem;
        }

        .stButton > button {
          background-color: var(--text-main);
          color: #FFFFFF;
          border: 1px solid var(--text-main);
          border-radius: 0;
          box-shadow: 3px 3px 0 0 var(--brand);
          font-family: 'Cabinet Grotesk', sans-serif;
          font-weight: 700;
          text-transform: uppercase;
          letter-spacing: 0.06em;
          padding: 0.55rem 1.1rem;
          transition: all 0.15s ease-in-out;
        }

        .stButton > button:hover {
          box-shadow: 5px 5px 0 0 var(--brand);
          transform: translate(-2px, -2px);
          color: #FFFFFF;
          border-color: var(--text-main);
        }

        .stButton > button:active {
          box-shadow: 0 0 0 0 var(--brand);
          transform: translate(3px, 3px);
        }

        .stButton > button:disabled {
          background: #C9C4B9;
          color: #666;
          box-shadow: none;
          border-color: #C9C4B9;
        }

        .stTextInput input,
        .stTextArea textarea,
        .stSelectbox > div > div,
        .stMultiSelect > div > div {
          border-radius: 0 !important;
          border: 1px solid var(--border) !important;
          background-color: #FFFFFF !important;
          font-family: 'General Sans', sans-serif !important;
        }

        .stTextInput input:focus,
        .stTextArea textarea:focus {
          border: 1px solid var(--text-main) !important;
          box-shadow: 2px 2px 0 0 var(--brand) !important;
          outline: none !important;
        }

        .stSlider [data-baseweb="slider"] > div > div {
          background: var(--text-main) !important;
        }

        .stSlider [role="slider"] {
          background: var(--brand) !important;
          border: 1px solid var(--text-main) !important;
        }

        .e1-card {
          background: var(--surface);
          border: 1px solid var(--border);
          border-radius: 4px;
          padding: 1.25rem 1.25rem 1.1rem;
          margin-bottom: 1rem;
          box-shadow: 2px 2px 0 0 rgba(17,17,17,0.05);
          height: 100%;
        }

        .e1-card .label {
          font-family: 'IBM Plex Mono', monospace;
          font-size: 0.7rem;
          text-transform: uppercase;
          letter-spacing: 0.12em;
          color: var(--text-tertiary);
          margin-bottom: 0.35rem;
        }

        .e1-card .value {
          font-family: 'Cabinet Grotesk', sans-serif;
          font-size: 1.1rem;
          font-weight: 700;
          color: var(--text-main);
          line-height: 1.35;
        }

        .e1-chip-row {
          display: flex;
          flex-wrap: wrap;
          gap: 0.4rem;
          margin-top: 0.4rem;
        }

        .e1-chip {
          font-family: 'IBM Plex Mono', monospace;
          font-size: 0.75rem;
          padding: 0.22rem 0.7rem;
          border-radius: 9999px;
          background: #FFFFFF;
          border: 1px solid var(--text-main);
          color: var(--text-main);
          font-weight: 500;
        }

        .e1-chip.positive {
          background: #E8F5E9;
          border-color: #2E7D32;
          color: #2E7D32;
        }

        .e1-chip.negative {
          background: #FFEBEE;
          border-color: #C62828;
          color: #C62828;
        }

        .e1-variation {
          background: var(--surface);
          border: 1px solid var(--text-main);
          padding: 1.25rem 1.4rem;
          margin-bottom: 1rem;
          box-shadow: 4px 4px 0 0 var(--brand);
        }

        .e1-variation .var-head {
          display: flex;
          justify-content: space-between;
          align-items: baseline;
          border-bottom: 1px solid var(--border);
          padding-bottom: 0.5rem;
          margin-bottom: 0.75rem;
        }

        .e1-variation .var-title {
          font-family: 'Cabinet Grotesk', sans-serif;
          font-weight: 800;
          font-size: 1rem;
          text-transform: uppercase;
          letter-spacing: 0.06em;
        }

        .e1-variation .var-meta {
          font-family: 'IBM Plex Mono', monospace;
          font-size: 0.72rem;
          color: var(--text-tertiary);
          text-transform: uppercase;
          letter-spacing: 0.08em;
        }

        .e1-variation .var-body {
          font-family: 'General Sans', sans-serif;
          font-size: 0.98rem;
          line-height: 1.6;
          color: var(--text-main);
          white-space: pre-wrap;
        }

        .e1-section-eyebrow {
          font-family: 'IBM Plex Mono', monospace;
          font-size: 0.72rem;
          text-transform: uppercase;
          letter-spacing: 0.14em;
          color: var(--brand);
          margin-bottom: 0.3rem;
        }

        .e1-status-pill {
          display: inline-block;
          padding: 0.28rem 0.75rem;
          font-family: 'IBM Plex Mono', monospace;
          font-size: 0.72rem;
          text-transform: uppercase;
          letter-spacing: 0.08em;
          border: 1px solid var(--text-main);
          border-radius: 9999px;
        }

        .e1-status-pill.ready {
          background: #E8F5E9;
          color: #2E7D32;
          border-color: #2E7D32;
        }

        .e1-status-pill.empty {
          background: #FFF;
          color: var(--text-secondary);
        }

        .e1-divider {
          border: none;
          border-top: 1px solid var(--border);
          margin: 2rem 0 1.5rem;
        }

        .streamlit-expanderHeader {
          font-family: 'Cabinet Grotesk', sans-serif;
          font-weight: 700;
        }

        .block-container {
          padding-top: 2rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ---------- HTML render helpers ----------
def _esc(v: Any) -> str:
    return html.escape("" if v is None else str(v))


def render_hero() -> None:
    st.markdown(
        """
        <div class="e1-hero" data-testid="app-hero">
          <div class="eyebrow">// AI Brand Voice Generator</div>
          <h1>Teach AI how your brand speaks.<br/>Create content that sounds like you.</h1>
          <div class="subtitle">
            Session-based brand voice conditioning — powered by Google Gemini.
          </div>
          <div class="desc">
            Analyze your existing content, build your unique brand voice profile,
            and generate original marketing content that stays consistent with
            your brand identity.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_attribute_card(
    label: str,
    value: str,
    testid: str = "voice-attr",
) -> str:
    return f"""
    <div class="e1-card" data-testid="{_esc(testid)}">
      <div class="label">{_esc(label)}</div>
      <div class="value">{_esc(value) or '—'}</div>
    </div>
    """


def render_chips(items: List[str], variant: str = "") -> str:
    if not items:
        return '<div class="e1-chip-row"><span class="e1-chip">—</span></div>'

    v = f" {variant}" if variant else ""

    chips = "".join(
        f'<span class="e1-chip{v}">{_esc(item)}</span>'
        for item in items
    )

    return f'<div class="e1-chip-row">{chips}</div>'


def render_variation_card(
    idx: int,
    text: str,
    content_type: str,
) -> str:
    word_count = len(text.split())
    char_count = len(text)

    return f"""
    <div class="e1-variation" data-testid="variation-card-{idx}">
      <div class="var-head">
        <div class="var-title">
          Variation {idx + 1} · {_esc(content_type)}
        </div>
        <div class="var-meta">
          {word_count} words · {char_count} chars
        </div>
      </div>
      <div class="var-body">{_esc(text)}</div>
    </div>
    """


def copy_button(text: str, key: str, testid: str) -> None:
    """A working copy-to-clipboard button using an HTML component."""
    safe = json.dumps(text)

    st.components.v1.html(
        f"""
        <div style="margin-top:-6px">
          <button id="btn-{key}" data-testid="{testid}"
            style="background:#FFFFFF;color:#111;border:1px solid #111;border-radius:0;
                   padding:0.4rem 0.9rem;font-family:'Cabinet Grotesk',sans-serif;font-weight:700;
                   text-transform:uppercase;letter-spacing:0.06em;font-size:0.75rem;
                   box-shadow:2px 2px 0 0 #111;cursor:pointer;">
            Copy
          </button>

          <span id="msg-{key}"
            style="margin-left:0.6rem;font-family:'IBM Plex Mono',monospace;
                   font-size:0.72rem;color:#2E7D32;visibility:hidden;">
            Copied to clipboard ✓
          </span>
        </div>

        <script>
        (function() {{
          const btn = document.getElementById("btn-{key}");
          const msg = document.getElementById("msg-{key}");

          if (!btn) return;

          btn.addEventListener("click", async () => {{
            const payload = {safe};

            try {{
              if (navigator.clipboard && window.isSecureContext) {{
                await navigator.clipboard.writeText(payload);
              }} else {{
                const ta = document.createElement("textarea");
                ta.value = payload;
                ta.style.position = "fixed";
                ta.style.opacity = "0";
                document.body.appendChild(ta);
                ta.select();
                document.execCommand("copy");
                document.body.removeChild(ta);
              }}

              msg.style.visibility = "visible";
              btn.innerText = "Copied ✓";

              setTimeout(() => {{
                msg.style.visibility = "hidden";
                btn.innerText = "Copy";
              }}, 1800);

            }} catch (e) {{
              msg.style.color = "#C62828";
              msg.innerText = "Copy failed — select text manually";
              msg.style.visibility = "visible";
            }}
          }});
        }})();
        </script>
        """,
        height=46,
    )


def profile_summary_dict(profile: Dict[str, Any]) -> Dict[str, str]:
    return {
        "Tone": profile.get("overall_tone", ""),
        "Personality": ", ".join(profile.get("personality", [])) or "—",
        "Formality": profile.get("formality", ""),
        "Emotion": profile.get("emotional_style", ""),
        "Vocabulary": profile.get("vocabulary_style", ""),
        "Writing Style": profile.get("sentence_style", ""),
        "Energy": profile.get("energy_level", ""),
        "CTA Style": profile.get("cta_style", ""),
        "Audience": profile.get("target_audience", ""),
    }
