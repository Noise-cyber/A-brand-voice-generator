"""AI Brand Voice Generator — Streamlit main entry point."""
from __future__ import annotations

from typing import Any, Dict, List

import streamlit as st

from config import (
    CONTENT_LENGTHS,
    CONTENT_TYPES,
    DEFAULTS,
    DEMO_SAMPLES,
    GEMINI_API_KEY,
    GEMINI_MODEL,
    MARKETING_GOALS,
    REFINEMENT_ACTIONS,
)
from gemini_service import (
    GeminiServiceError,
    analyze_brand_voice,
    generate_content,
    initialize_gemini,
    refine_content,
    validate_brand_samples,
    validate_generation_input,
)
from utils import (
    copy_button,
    init_session_state,
    load_css,
    profile_summary_dict,
    render_attribute_card,
    render_chips,
    render_hero,
    render_variation_card,
    reset_session,
)


# ============================================================
# Page setup
# ============================================================
st.set_page_config(
    page_title="AI Brand Voice Generator",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)
load_css()
init_session_state()


# ============================================================
# Sidebar
# ============================================================
def render_sidebar() -> Dict[str, Any]:
    with st.sidebar:
        st.markdown("### Brand Settings")
        meta = st.session_state["brand_meta"]
        meta["brand_name"] = st.text_input(
            "Brand Name", value=meta.get("brand_name", ""), key="sb_brand_name",
        )
        meta["industry"] = st.text_input(
            "Industry", value=meta.get("industry", ""), key="sb_industry",
        )
        meta["audience"] = st.text_input(
            "Target Audience", value=meta.get("audience", ""), key="sb_audience",
        )
        meta["description"] = st.text_area(
            "Brand Description",
            value=meta.get("description", ""),
            key="sb_description",
            height=90,
        )
        st.session_state["brand_meta"] = meta

        st.markdown("<hr class='e1-divider'/>", unsafe_allow_html=True)
        st.markdown("### Generation Settings")
        default_creativity = st.slider(
            "Default Creativity",
            0.0, 1.0, DEFAULTS.creativity, 0.05,
            key="sb_creativity",
        )
        default_length = st.select_slider(
            "Default Content Length",
            options=CONTENT_LENGTHS,
            value=DEFAULTS.length,
            key="sb_length",
        )
        default_variations = st.number_input(
            "Default Variations", min_value=1, max_value=5,
            value=DEFAULTS.variations, step=1, key="sb_variations",
        )

        st.markdown("<hr class='e1-divider'/>", unsafe_allow_html=True)
        st.markdown("### Session")
        if st.session_state["brand_profile"]:
            st.markdown(
                '<span class="e1-status-pill ready" data-testid="profile-status-ready">'
                'Brand Voice Profile Ready ✓</span>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<span class="e1-status-pill empty" data-testid="profile-status-empty">'
                'No profile loaded</span>',
                unsafe_allow_html=True,
            )

        if st.button("Reset Brand Profile", key="sb_reset", use_container_width=True):
            reset_session()
            st.rerun()

        st.markdown("<hr class='e1-divider'/>", unsafe_allow_html=True)
        st.markdown("### Model")
        st.markdown(
            f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:0.78rem;'
            f'color:#555;">MODEL: <b>{GEMINI_MODEL}</b><br/>'
            f'API KEY: <b>{"detected ✓" if GEMINI_API_KEY else "missing ✗"}</b></div>',
            unsafe_allow_html=True,
        )

    return {
        "creativity": default_creativity,
        "length": default_length,
        "variations": int(default_variations),
    }


# ============================================================
# Step 1 — Teach Voice
# ============================================================
def render_step_teach_voice() -> None:
    st.markdown('<div class="e1-section-eyebrow">// Step 01</div>', unsafe_allow_html=True)
    st.markdown("## Teach Your Brand Voice")
    st.markdown(
        "<div style='color:#555;max-width:720px;margin-bottom:1rem;'>Paste real examples of "
        "how your brand already speaks — social posts, emails, taglines, product copy. "
        "The more variety, the sharper the voice profile.</div>",
        unsafe_allow_html=True,
    )

    # Demo loader
    demo_cols = st.columns([2, 2, 2, 2])
    demo_cols[0].markdown(
        "<div style='font-family:\"IBM Plex Mono\",monospace;font-size:0.72rem;"
        "color:#888;text-transform:uppercase;letter-spacing:0.1em;padding-top:0.5rem;'>"
        "Try a demo:</div>",
        unsafe_allow_html=True,
    )
    for i, demo in enumerate(DEMO_SAMPLES):
        if demo_cols[i + 1].button(demo.label, key=f"demo_{i}", use_container_width=True):
            st.session_state["samples"] = demo.samples
            st.session_state["brand_meta"] = {
                "brand_name": demo.brand_name,
                "industry": demo.industry,
                "audience": demo.audience,
                "description": demo.description,
            }
            st.rerun()

    st.text_area(
        label="Paste your existing brand content here...",
        key="samples",
        height=260,
        placeholder=(
            "Paste multiple examples separated by blank lines. Examples:\n\n"
            "• Social media posts\n"
            "• Instagram captions\n"
            "• Marketing emails\n"
            "• Taglines\n"
            "• Ad copy\n"
            "• Product descriptions\n"
            "• Blog intros\n"
            "• Website copy"
        ),
    )

    analyze_col, info_col = st.columns([1, 3])
    with analyze_col:
        analyze_clicked = st.button(
            "Analyze Brand Voice",
            key="btn_analyze",
            use_container_width=True,
        )
    with info_col:
        st.markdown(
            "<div style='font-family:\"IBM Plex Mono\",monospace;font-size:0.75rem;"
            "color:#888;padding-top:0.55rem;'>Session-based conditioning · no fine-tuning · "
            "your data isn't stored beyond this session.</div>",
            unsafe_allow_html=True,
        )

    if analyze_clicked:
        samples = st.session_state.get("samples", "")
        ok, msg = validate_brand_samples(samples, DEFAULTS.min_sample_chars)
        if not ok:
            st.warning(msg)
            return
        try:
            initialize_gemini()  # early failure if key is missing
        except GeminiServiceError as exc:
            st.error(str(exc))
            return
        meta = st.session_state["brand_meta"]
        with st.spinner("Analyzing your brand's voice with Gemini..."):
            try:
                profile = analyze_brand_voice(
                    samples=samples,
                    brand_name=meta.get("brand_name", ""),
                    industry=meta.get("industry", ""),
                    audience=meta.get("audience", ""),
                    description=meta.get("description", ""),
                )
                st.session_state["brand_profile"] = profile
                # Analysis invalidates prior generations
                st.session_state["generated_variations"] = []
                st.session_state["generation_meta"] = None
                st.success("Brand Voice Profile ready. Scroll down to generate content.")
            except GeminiServiceError as exc:
                st.error(f"Analysis failed: {exc}")
            except Exception as exc:  # pragma: no cover
                st.error(f"Unexpected error: {exc}")


# ============================================================
# Brand Voice Profile UI
# ============================================================
def render_profile() -> None:
    profile = st.session_state.get("brand_profile")
    if not profile:
        return

    st.markdown("<hr class='e1-divider'/>", unsafe_allow_html=True)
    st.markdown('<div class="e1-section-eyebrow">// Profile</div>', unsafe_allow_html=True)
    header_col, action_col = st.columns([3, 1])
    header_col.markdown("## Your Brand Voice")
    with action_col:
        if st.button("Re-analyze Voice", key="btn_reanalyze", use_container_width=True):
            st.session_state["brand_profile"] = None
            st.session_state["generated_variations"] = []
            st.session_state["generation_meta"] = None
            st.rerun()

    summary = profile_summary_dict(profile)
    keys = list(summary.keys())
    # 3-col grid, 3 rows
    for row_start in range(0, len(keys), 3):
        cols = st.columns(3)
        for offset, col in enumerate(cols):
            if row_start + offset >= len(keys):
                continue
            k = keys[row_start + offset]
            col.markdown(
                render_attribute_card(k, summary[k], testid=f"voice-attr-{k.lower().replace(' ', '-')}"),
                unsafe_allow_html=True,
            )

    # Preferred / Avoid words + brand characteristics
    left, right = st.columns(2)
    with left:
        st.markdown('<div class="e1-section-eyebrow">// Vocabulary</div>', unsafe_allow_html=True)
        st.markdown("### Words & Phrases to Prefer")
        st.markdown(
            render_chips(
                profile.get("preferred_words", []) + profile.get("preferred_phrases", []),
                variant="positive",
            ),
            unsafe_allow_html=True,
        )
    with right:
        st.markdown('<div class="e1-section-eyebrow">// Guardrails</div>', unsafe_allow_html=True)
        st.markdown("### Words & Phrases to Avoid")
        st.markdown(
            render_chips(profile.get("avoid_words", []), variant="negative"),
            unsafe_allow_html=True,
        )

    st.markdown('<div class="e1-section-eyebrow" style="margin-top:1.2rem;">// Characteristics</div>', unsafe_allow_html=True)
    st.markdown("### Brand Communication Characteristics")
    st.markdown(render_chips(profile.get("brand_characteristics", [])), unsafe_allow_html=True)

    with st.expander("View raw JSON profile"):
        st.json(profile)


# ============================================================
# Step 2 — Generate Content
# ============================================================
def render_generation(defaults: Dict[str, Any]) -> None:
    st.markdown("<hr class='e1-divider'/>", unsafe_allow_html=True)
    st.markdown('<div class="e1-section-eyebrow">// Step 02</div>', unsafe_allow_html=True)
    st.markdown("## Generate Brand Content")

    profile_ready = bool(st.session_state.get("brand_profile"))
    if not profile_ready:
        st.info("Complete Step 01 first — an analyzed Brand Voice Profile unlocks content generation.")

    top = st.columns([1, 1, 1])
    content_type = top[0].selectbox("Content Format", CONTENT_TYPES, key="gen_type")
    goal = top[1].selectbox("Marketing Goal", MARKETING_GOALS, key="gen_goal")
    audience = top[2].text_input(
        "Target Audience",
        value=st.session_state["brand_meta"].get("audience", ""),
        key="gen_audience",
        placeholder="e.g. College students and young professionals",
    )

    topic = st.text_input(
        "Topic / Product",
        key="gen_topic",
        placeholder="e.g. Launching our new AI productivity app",
    )
    extra = st.text_area(
        "Additional Instructions (optional)",
        key="gen_extra",
        height=90,
        placeholder="e.g. Keep it energetic and end with a strong CTA.",
    )

    ctrl = st.columns([1, 2, 1])
    length = ctrl[0].select_slider(
        "Content Length", options=CONTENT_LENGTHS, value=defaults["length"], key="gen_length",
    )
    creativity = ctrl[1].slider(
        "Creativity", 0.0, 1.0, defaults["creativity"], 0.05, key="gen_creativity",
    )
    variations = ctrl[2].number_input(
        "Variations", min_value=1, max_value=5, value=defaults["variations"], step=1, key="gen_variations",
    )

    generate_clicked = st.button(
        "Generate Content",
        key="btn_generate",
        disabled=not profile_ready,
        use_container_width=False,
    )

    if generate_clicked:
        ok, msg = validate_generation_input(topic)
        if not ok:
            st.warning(msg)
            return
        with st.spinner("Generating content in your brand voice..."):
            try:
                variations_out = generate_content(
                    profile=st.session_state["brand_profile"],
                    content_type=content_type,
                    topic=topic,
                    goal=goal,
                    audience=audience,
                    extra_instructions=extra,
                    length=length,
                    creativity=creativity,
                    variations=int(variations),
                )
                st.session_state["generated_variations"] = variations_out
                st.session_state["generation_meta"] = {
                    "content_type": content_type,
                    "goal": goal,
                    "topic": topic,
                    "audience": audience,
                    "extra": extra,
                    "length": length,
                    "creativity": creativity,
                }
                st.session_state["refining_index"] = None
            except GeminiServiceError as exc:
                st.error(f"Generation failed: {exc}")
            except Exception as exc:  # pragma: no cover
                st.error(f"Unexpected error: {exc}")


# ============================================================
# Generated variations + Refinement
# ============================================================
def render_variations() -> None:
    variations: List[str] = st.session_state.get("generated_variations") or []
    meta = st.session_state.get("generation_meta")
    if not variations or not meta:
        return

    st.markdown("<hr class='e1-divider'/>", unsafe_allow_html=True)
    st.markdown('<div class="e1-section-eyebrow">// Results</div>', unsafe_allow_html=True)
    st.markdown("## Generated Variations")
    st.markdown(
        f"<div style='color:#555;margin-bottom:1rem;'>{len(variations)} on-brand "
        f"{meta['content_type'].lower()}(s) for goal: <b>{meta['goal']}</b>.</div>",
        unsafe_allow_html=True,
    )

    for idx, text in enumerate(variations):
        st.markdown(
            render_variation_card(idx, text, meta["content_type"]),
            unsafe_allow_html=True,
        )
        action_cols = st.columns([1, 1, 1, 5])
        with action_cols[0]:
            copy_button(text, key=f"copy_{idx}", testid=f"copy-btn-{idx}")
        with action_cols[1]:
            if st.button("Refine", key=f"refine_open_{idx}", use_container_width=True):
                st.session_state["refining_index"] = (
                    None if st.session_state.get("refining_index") == idx else idx
                )
                st.rerun()
        with action_cols[2]:
            if st.button("Regenerate", key=f"regen_{idx}", use_container_width=True):
                _regenerate_single(idx)
                st.rerun()

        if st.session_state.get("refining_index") == idx:
            _render_refine_panel(idx, text, meta)


def _regenerate_single(idx: int) -> None:
    meta = st.session_state.get("generation_meta")
    profile = st.session_state.get("brand_profile")
    if not meta or not profile:
        return
    with st.spinner("Regenerating this variation..."):
        try:
            new_batch = generate_content(
                profile=profile,
                content_type=meta["content_type"],
                topic=meta["topic"],
                goal=meta["goal"],
                audience=meta["audience"],
                extra_instructions=meta["extra"],
                length=meta["length"],
                creativity=min(1.0, meta["creativity"] + 0.1),
                variations=1,
            )
            if new_batch:
                variations = list(st.session_state["generated_variations"])
                variations[idx] = new_batch[0]
                st.session_state["generated_variations"] = variations
        except GeminiServiceError as exc:
            st.error(f"Regeneration failed: {exc}")


def _render_refine_panel(idx: int, current_text: str, meta: Dict[str, Any]) -> None:
    with st.container():
        st.markdown(
            f'<div class="e1-section-eyebrow" style="margin-top:0.5rem;">// Refine Variation {idx + 1}</div>',
            unsafe_allow_html=True,
        )
        selected = st.multiselect(
            "Quick actions",
            REFINEMENT_ACTIONS,
            key=f"refine_actions_{idx}",
        )
        custom = st.text_area(
            "Custom feedback",
            key=f"refine_custom_{idx}",
            height=80,
            placeholder="Tell AI how you want to improve this content...",
        )
        cols = st.columns([1, 1, 4])
        run = cols[0].button("Refine Content", key=f"refine_run_{idx}")
        cancel = cols[1].button("Cancel", key=f"refine_cancel_{idx}")

        if cancel:
            st.session_state["refining_index"] = None
            st.rerun()

        if run:
            profile = st.session_state.get("brand_profile") or {}
            with st.spinner("Refining your content..."):
                try:
                    refined = refine_content(
                        profile=profile,
                        current_content=current_text,
                        refinement_actions=selected,
                        custom_feedback=custom,
                        content_type=meta["content_type"],
                        goal=meta["goal"],
                    )
                    variations = list(st.session_state["generated_variations"])
                    variations[idx] = refined
                    st.session_state["generated_variations"] = variations
                    st.session_state["refining_index"] = None
                    st.success("Content refined.")
                    st.rerun()
                except GeminiServiceError as exc:
                    st.error(f"Refinement failed: {exc}")


# ============================================================
# About
# ============================================================
def render_about() -> None:
    st.markdown("<hr class='e1-divider'/>", unsafe_allow_html=True)
    st.markdown('<div class="e1-section-eyebrow">// About</div>', unsafe_allow_html=True)
    st.markdown("## What is AI Brand Voice Generator?")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            """
This app uses **Google Gemini** to analyze examples of your existing brand
communication and reproduce the underlying writing characteristics when
generating new marketing content.

**Who can use it?**
- Marketers & founders
- Freelancers & content creators
- Marketing agencies
- Students & small businesses

**Main Benefits**
- Faster content creation
- Consistent brand communication
- 11 content formats out of the box
- Easy refinement with quick actions
- Reduced repetitive writing
            """
        )
    with col2:
        st.markdown(
            """
### Use Case 1 — Marketing & Content Creation
A startup provides existing taglines, ads, emails, and social posts. The AI
analyzes the communication style and generates new Instagram posts, product
announcements, marketing emails, ad copy, and taglines — all in the same voice.

### Use Case 2 — Personalized Branding for Agencies
Freelancers and agencies can maintain a different profile per client. A
lifestyle brand stays playful and casual, a B2B tech brand stays professional
and confident — from the same tool.
            """
        )

    st.info(
        "This is session-based brand voice conditioning, not model fine-tuning. "
        "Your brand profile is stored in your browser session only and disappears "
        "when you reset or close the tab."
    )


# ============================================================
# Main
# ============================================================
def main() -> None:
    render_hero()
    if not GEMINI_API_KEY:
        st.error(
            "GEMINI_API_KEY is not configured. Create a `.env` file in `streamlit_app/` "
            "with `GEMINI_API_KEY=your_api_key_here` and restart, or set it via Streamlit secrets."
        )
    defaults = render_sidebar()
    render_step_teach_voice()
    render_profile()
    render_generation(defaults)
    render_variations()
    render_about()


if __name__ == "__main__":
    main()
