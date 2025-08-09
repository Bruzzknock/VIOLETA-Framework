import json
import streamlit as st
import app_utils
import ai

st.header("Step 3A - Kernel Analogies")

skill_kernels = app_utils.load_skill_kernels()
kernel_benefits = app_utils.load_kernel_benefits() or {}
benefit_mappings = app_utils.load_kernel_benefit_mappings() or []

# Build a flattened list of kernels enriched with their "why it matters" benefits
kernels_with_benefits: list = []
if isinstance(skill_kernels, dict):
    benefit_lookup: dict[str, list[str]] = {}
    for mapping in benefit_mappings:
        kid = mapping.get("kernel_id")
        bid = mapping.get("benefit_id")
        if kid and bid and bid in kernel_benefits:
            text = kernel_benefits[bid]
            if mapping.get("copy_override"):
                text = mapping["copy_override"]
            benefit_lookup.setdefault(kid, []).append(text)
    for skill, kern_list in skill_kernels.items():
        if isinstance(kern_list, list):
            for kern in kern_list:
                enriched = dict(kern)
                benefits = benefit_lookup.get(kern.get("id"), [])
                if benefits:
                    enriched["why_it_matters"] = benefits
                enriched["skill"] = skill
                kernels_with_benefits.append(enriched)
else:
    if isinstance(skill_kernels, list):
        kernels_with_benefits = skill_kernels

# Session state for progress
if "kernel_index" not in st.session_state:
    st.session_state.kernel_index = 0
if "kernel_analogies" not in st.session_state:
    st.session_state.kernel_analogies = app_utils.load_kernel_analogies() or {}
if "generated_analogies" not in st.session_state:
    st.session_state.generated_analogies = []


def parse_analogies(text: str) -> list[str]:
    blocks: list[str] = []
    current: list[str] = []
    for line in text.strip().splitlines():
        if line.startswith("Analogy"):
            if current:
                blocks.append("\n".join(current).strip())
                current = []
        current.append(line)
    if current:
        blocks.append("\n".join(current).strip())
    return [b for b in blocks if b]


total = len(kernels_with_benefits)
if st.session_state.kernel_index < total:
    k = kernels_with_benefits[st.session_state.kernel_index]
    st.subheader(f"Kernel {st.session_state.kernel_index + 1} of {total}")
    st.markdown(f"**{k.get('kernel', '')}**")
    setting = st.text_input(
        "Optional setting for generated analogies (e.g., fantasy, sci-fi)",
        key="analogy_setting",
    )
    manual = st.text_area("Write your own analogies (one per line)", key="manual_analogy")


    if st.button("Generate analogies"):
        with st.spinner("Generating analogies..."):
            raw = ai.step3a(k, setting=setting)
        st.session_state.generated_analogies = parse_analogies(raw)

    for idx, ana in enumerate(st.session_state.generated_analogies):
        st.checkbox(f"Select Analogy {idx + 1}", key=f"gen_{idx}")
        st.markdown(ana)

    if st.button("Save and Next"):
        selected: list[str] = []
        for idx, ana in enumerate(st.session_state.generated_analogies):
            if st.session_state.get(f"gen_{idx}"):
                selected.append(ana)
            if f"gen_{idx}" in st.session_state:
                del st.session_state[f"gen_{idx}"]

        manual_list = [line.strip() for line in manual.splitlines() if line.strip()]
        selected.extend(manual_list)

        key = k.get("id") or k.get("kernel")
        st.session_state.kernel_analogies[key] = {
            "kernel": k.get("kernel"),
            "skill": k.get("skill"),
            "analogies": selected,
        }
        app_utils.save_kernel_analogies(st.session_state.kernel_analogies)
        st.session_state.kernel_index += 1
        st.session_state.generated_analogies = []
        st.session_state.manual_analogy = ""
        st.session_state.analogy_setting = ""
        st.experimental_rerun()
else:
    st.success("All kernels processed.")
    st.subheader("Selected Analogies")
    for item in st.session_state.kernel_analogies.values():
        st.markdown(f"**{item.get('kernel', '')}**")
        for ana in item.get("analogies", []):
            st.write(ana)

st.header("Step 3B - Theme & Kernel Mapping")

theme = app_utils.load_theme()
theme_name = app_utils.load_theme_name()

with st.form("step3_form"):
    theme_input = st.text_area(
        "Write a two-sentence mood blurb describing a world or situation where these skills are used regularly:",
        value=theme,
        height=80,
    )
    theme_name_input = st.text_input(
        "Provide a short name for this theme:",
        value=theme_name,
    )
    submitted = st.form_submit_button("Save Theme")

if submitted:
    app_utils.save_theme(theme_input)
    app_utils.save_theme_name(theme_name_input)

st.subheader("Kernel Mapping Table")

if "info_text" not in st.session_state:
    loaded = app_utils.load_kernel_theme_mapping()
    if loaded:
        st.session_state.info_text = json.dumps(loaded, indent=2)
    else:
        st.session_state.info_text = ""

st.text_area("Step 3B Table (JSON)", key="info_text", height=200)

if st.button("Save Additional Info"):
    app_utils.save_kernel_theme_mapping(st.session_state.info_text)
