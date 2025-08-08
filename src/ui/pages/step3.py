import json
import streamlit as st
import app_utils
import ai

st.header("Step 3 - Theme & Kernel Mapping")

atomic_skills = app_utils.load_atomic_skills()
skill_kernels = app_utils.load_skill_kernels()
kernel_benefits = app_utils.load_kernel_benefits() or {}
benefit_mappings = app_utils.load_kernel_benefit_mappings() or []

# Build kernels enriched with their "why it matters" benefits
kernels_with_benefits: dict = {}
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
        new_list = []
        if isinstance(kern_list, list):
            for kern in kern_list:
                enriched = dict(kern)
                benefits = benefit_lookup.get(kern.get("id"), [])
                if benefits:
                    enriched["why_it_matters"] = benefits
                new_list.append(enriched)
        kernels_with_benefits[skill] = new_list
else:
    kernels_with_benefits = skill_kernels

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

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    st.chat_message(message["role"]).write(message["content"])

prompt = st.chat_input("Generate Ideas")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.spinner("Generating answer..."):
        answer = ai.step3(
            atomic_skills,
            skill_kernels,
            kernels_with_benefits,
            st.session_state.messages,
        )
    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.chat_message("user").write(prompt)
    st.chat_message("assistant").write(answer)
