import streamlit as st
import time
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

generate = st.button("Generate Ideas")

if(generate):
    atomic_unit = ai.step1()
    atomic_unit

prompt = st.chat_input("Ask for help!")

if prompt:
    st.write(f"The user has sent: {prompt}")