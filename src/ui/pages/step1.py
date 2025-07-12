import streamlit as st
import app_utils
import ai

st.header("Step 1 - Atomic unit")

with st.form("step1_form"):
    atmoic_unit_input = st.text_input(
        "What is the atomic unit that the game should be based on?"
    )
    submitted = st.form_submit_button("Next")

if submitted:
    app_utils.save(atmoic_unit_input)

if "messages" not in st.session_state:
    st.session_state.messages = []

generate = st.button("Generate Ideas")
if generate:
    answer = ai.step1(st.session_state.messages)
    st.session_state.messages.append({"role": "assistant", "content": answer})

for message in st.session_state.messages:
    st.chat_message(message["role"]).write(message["content"])

prompt = st.chat_input("Ask for help!")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    answer = ai.step1(st.session_state.messages)
    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.chat_message("user").write(prompt)
    st.chat_message("assistant").write(answer)
