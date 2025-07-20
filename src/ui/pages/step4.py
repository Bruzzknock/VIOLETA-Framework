import json
import streamlit as st
import app_utils
import ai

st.header("Step 4 - Map the Emotional Arc")

atomic_skills = app_utils.load_atomic_skills()
theme = app_utils.load_theme()

stored = app_utils.load_emotional_arc()

vignette_default = stored.get("vignette", "") if stored else ""
feelings_default = stored.get("feelings", "") if stored else ""

with st.form("step4_form"):
    vignette_input = st.text_area(
        "Write a short vignette describing the player's emotional journey:",
        value=vignette_default,
        height=80,
    )
    feelings_input = st.text_area(
        "List the key feelings to evoke (one per line or JSON list):",
        value=feelings_default,
        height=80,
    )
    submitted = st.form_submit_button("Save Emotional Arc")

if submitted:
    app_utils.save_emotional_arc(vignette_input, feelings_input)

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    st.chat_message(message["role"]).write(message["content"])

prompt = st.chat_input("Generate Ideas")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.spinner("Generating answer..."):
        answer = ai.step4(theme, atomic_skills, st.session_state.messages)
    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.chat_message("user").write(prompt)
    st.chat_message("assistant").write(answer)

