import streamlit as st
import app_utils
import ai

st.header("Step 2 - Atomic Skills")

atomic_unit = app_utils.load("TODO")

generate = st.button("Generate Ideas")

if(generate):
    atomic_skills = ai.step2(atomic_unit)
    atomic_skills