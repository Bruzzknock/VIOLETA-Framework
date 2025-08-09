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

if "info_text" not in st.session_state:
    loaded = app_utils.load_kernel_theme_mapping()
    if loaded:
        st.session_state.info_text = json.dumps(loaded, indent=2)
    else:
        st.session_state.info_text = ""

st.text_area("Step 3B Table (JSON)", key="info_text", height=200)

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