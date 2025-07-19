import json
import streamlit as st
import app_utils
import ai

st.header("Step 3 - Theme & Kernel Mapping")

atomic_skills = app_utils.load_atomic_skills()
skill_kernels = app_utils.load_skill_kernels()
theme = app_utils.load_theme()

with st.form("step3_form"):
    theme_input = st.text_area(
        "Write a two-sentence mood blurb describing a world or situation where these skills are used regularly:",
        value=theme,
        height=80,
    )
    submitted = st.form_submit_button("Save Theme")

if submitted:
    app_utils.save_theme(theme_input)

st.subheader("Kernel Mapping Table")

if "info_text" not in st.session_state:
    loaded = app_utils.load_kernel_theme_mapping()
    if loaded:
        st.session_state.info_text = json.dumps(loaded, indent=2)
    else:
        st.session_state.info_text = ""

st.text_area("Step 3B Table (JSON)", key="info_text", height=200)

def generate_mapping():
    with st.spinner("Generating mapping..."):
        generated = ai.step3_mapping(theme_input, skill_kernels)
    st.session_state.info_text = generated

st.button("Generate Mapping", on_click=generate_mapping)

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
        answer = ai.step3(atomic_skills, skill_kernels, st.session_state.messages)
    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.chat_message("user").write(prompt)
    st.chat_message("assistant").write(answer)
