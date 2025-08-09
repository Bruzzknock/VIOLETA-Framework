import json
import streamlit as st
import app_utils
import ai

atomic_unit = app_utils.load_atomic_unit()
atomic_skills = app_utils.load_atomic_skills()

if "messages" not in st.session_state:
    st.session_state.messages = []

st.header("Step 3 - Theme & Kernel Mapping")

theme = app_utils.load_theme()
theme_name = app_utils.load_theme_name()

with st.form("step3_form"):
    theme_input = st.text_area(
        "Write a two-paragraph mood blurb describing a world or situation where these skills are used regularly:",
        value=theme,
        height=120,
    )
    theme_name_input = st.text_input(
        "Provide a short name for this theme:",
        value=theme_name,
    )
    submitted = st.form_submit_button("Save Theme")

if submitted:
    app_utils.save_theme(theme_input)
    app_utils.save_theme_name(theme_name_input)

for message in st.session_state.messages:
    st.chat_message(message["role"]).write(message["content"])

prompt = st.chat_input("Generate Ideas")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.spinner("Generating answer..."):
        answer = ai.step3a(atomic_unit, atomic_skills, st.session_state.messages)
    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.chat_message("user").write(prompt)
    st.chat_message("assistant").write(answer)

# ---------------------------------------------------------------------------
# Step 3B – Kernel Theme Mapping

st.subheader("Kernel Theme Mapping")

loaded_mapping = app_utils.load_kernel_theme_mapping()
if "kernel_theme_text" not in st.session_state:
    if loaded_mapping:
        st.session_state.kernel_theme_text = json.dumps(loaded_mapping, indent=2)
    else:
        st.session_state.kernel_theme_text = ""

st.text_area(
    "Provide or edit the kernel theme mapping as JSON",
    key="kernel_theme_text",
    height=300,
)


def generate_kernel_theme_mapping():
    theme_val = app_utils.load_theme()
    skill_kernels = app_utils.load_skill_kernels()
    benefits = app_utils.load_kernel_benefits() or {}
    benefit_maps = app_utils.load_kernel_benefit_mappings() or []

    kernels_list = []
    if isinstance(skill_kernels, dict):
        for kern_list in skill_kernels.values():
            if isinstance(kern_list, list):
                for kern in kern_list:
                    kern_benefits = [
                        m.get("copy_override") or benefits.get(m.get("benefit_id"))
                        for m in benefit_maps
                        if m.get("kernel_id") == kern.get("id")
                        and m.get("benefit_id") in benefits
                    ]
                    kernels_list.append(
                        {
                            "kernel": kern.get("kernel", ""),
                            "original_input": kern.get("input", ""),
                            "original_verb": kern.get("verb", ""),
                            "original_output": kern.get("output", ""),
                            "learning_type": kern.get("learning_type", ""),
                            "benefits": kern_benefits,
                        }
                    )

    mapping = ai.step3b_all(theme_val, kernels_list)
    st.session_state.kernel_theme_text = json.dumps(mapping, indent=2)
    app_utils.save_kernel_theme_mapping(st.session_state.kernel_theme_text)


st.button("Generate Kernel Theme Mapping", on_click=generate_kernel_theme_mapping)

if st.button("Save Kernel Theme Mapping"):
    app_utils.save_kernel_theme_mapping(st.session_state.kernel_theme_text)
