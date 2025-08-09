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

st.subheader("Kernel Mapping Table")

# Initialise storage for generated mappings and raw JSON
if "kernel_mappings" not in st.session_state:
    loaded = app_utils.load_kernel_theme_mapping()
    if isinstance(loaded, dict):
        st.session_state.kernel_mappings = loaded.get("kernels", [])
        st.session_state.info_text = json.dumps(loaded, indent=2)
    else:
        st.session_state.kernel_mappings = []
        st.session_state.info_text = ""

# Display mappings in a readable format
if st.session_state.kernel_mappings:
    for item in st.session_state.kernel_mappings:
        title = item.get("kernel", "Kernel")
        with st.expander(title):
            st.markdown(f"**In-world:** {item.get('in_world_kernel_sentence', '')}")
            st.markdown(
                f"**Input:** {item.get('original_input', '')} → {item.get('in_world_input', '')}"
            )
            st.markdown(
                f"**Verb:** {item.get('original_verb', '')} → {item.get('in_world_verb', '')}"
            )
            st.markdown(
                f"**Output:** {item.get('original_output', '')} → {item.get('in_world_output', '')}"
            )
            if item.get("benefit_mapping"):
                st.markdown("**Benefits:**")
                for b in item["benefit_mapping"]:
                    st.markdown(
                        f"- {b.get('benefit')}: {b.get('in_world_effect')}"
                    )
else:
    st.write("No kernel mappings generated yet.")

with st.expander("Raw JSON"):
    st.text_area("Step 3B Table (JSON)", key="info_text", height=200)


def generate_kernel_mappings():
    theme_text = app_utils.load_theme()
    skill_kernels = app_utils.load_skill_kernels()
    benefits = app_utils.load_kernel_benefits() or {}
    benefit_mappings = app_utils.load_kernel_benefit_mappings() or []

    all_kernels: list[dict] = []
    if isinstance(skill_kernels, dict):
        for kern_list in skill_kernels.values():
            if isinstance(kern_list, list):
                all_kernels.extend(kern_list)

    for idx, kernel in enumerate(all_kernels, start=1):
        if isinstance(kernel, dict):
            kernel.setdefault("id", f"k{idx}")
            btexts = []
            for m in benefit_mappings:
                if m.get("kernel_id") == kernel.get("id"):
                    text = benefits.get(m.get("benefit_id"), "")
                    if m.get("copy_override"):
                        text = m["copy_override"]
                    if text:
                        btexts.append(text)
            if btexts:
                kernel["benefits"] = btexts

    results = []
    with st.spinner("Generating kernels..."):
        for kernel in all_kernels:
            generated = ai.step3b(theme_text, [kernel])
            try:
                parsed = json.loads(generated)
                if isinstance(parsed, dict):
                    items = parsed.get("kernels")
                    if isinstance(items, list) and items:
                        results.append(items[0])
            except Exception:
                continue
    st.session_state.kernel_mappings = results
    st.session_state.info_text = json.dumps({"kernels": results}, indent=2)


st.button("Generate Kernels", on_click=generate_kernel_mappings)

if st.button("Save Additional Info"):
    app_utils.save_kernel_theme_mapping(st.session_state.info_text)

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
