import streamlit as st
import app_utils
import ai

st.header("Step 2 - Atomic Skills")

atomic_unit = app_utils.load_atomic_unit()

with st.form("step2_form"):
    atmoic_skills_input = st.text_input(
        "What knowledge, actions, and/or skills are necessary to master this atomic unit?"
    )
    submitted = st.form_submit_button("Next")

if submitted:
    app_utils.save_atomic_skills(atmoic_skills_input)

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    st.chat_message(message["role"]).write(message["content"])

prompt = st.chat_input("Generate Ideas")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    answer = ai.step2(atomic_unit, st.session_state.messages)
    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.chat_message("user").write(prompt)
    st.chat_message("assistant").write(answer)