import streamlit as st
import time
from ui import app_utils

st.header("Step 1 - Atomic unit")

with st.form("step1_form"):
    atmoic_unit_input = st.text_input(
            "What is the atomic unit that the game should be based on?"
        )
    submitted = st.form_submit_button("Next")

if submitted:
    save(atmoic_unit_input)