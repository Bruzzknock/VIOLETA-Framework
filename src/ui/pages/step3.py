import streamlit as st
import app_utils
import ai

st.header("Step 3 - Theme")

atomic_skills = app_utils.load_atomic_skills()

with st.form("step3_form"):
    theme_input = st.text_input(
        "“In what kind of world or situation would someone need to use the skills from my atomic unit regularly?”"
    )
    submitted = st.form_submit_button("Next")

if submitted:
    app_utils.save_atomic_skills(theme_input)

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    st.chat_message(message["role"]).write(message["content"])

prompt = st.chat_input("Generate Ideas")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    answer = ai.step3(atomic_skills, st.session_state.messages)
    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.chat_message("user").write(prompt)
    st.chat_message("assistant").write(answer)