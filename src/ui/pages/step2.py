import json
import streamlit as st
import app_utils
import ai

st.header("Step 2 - Atomic Skills & Kernels")

atomic_unit = app_utils.load_atomic_unit()
learning_types = app_utils.load_learning_types()
if learning_types:
    st.write("Learning Types: " + ", ".join(learning_types))

with st.form("step2_form"):
    atomic_skills_input = st.text_area(
        "What knowledge, actions, and/or skills are necessary to master this atomic unit?\n\n"
        "You can group skills by entering a category name followed by its skills on separate lines.\n"
        "Leave a blank line between categories.",
        height=200,
    )
    submitted = st.form_submit_button("Next")

if submitted:
    app_utils.save_atomic_skills(atomic_skills_input)

st.subheader("Skill Kernels")

loaded_kernels = app_utils.load_skill_kernels()
if "kernels_text" not in st.session_state:
    if loaded_kernels:
        st.session_state.kernels_text = json.dumps(loaded_kernels, indent=2)
    else:
        st.session_state.kernels_text = ""

st.text_area(
    "Provide a one-sentence kernel for each skill using JSON mapping",
    key="kernels_text",
    height=200,
)

def generate_kernels():
    with st.spinner("Generating kernels..."):
        generated = ai.step2_kernels(
            atomic_unit, app_utils.load_atomic_skills()
        )
    st.session_state.kernels_text = generated

st.button("Generate Kernels", on_click=generate_kernels)

if st.button("Save Kernels"):
    app_utils.save_skill_kernels(st.session_state.kernels_text)

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    st.chat_message(message["role"]).write(message["content"])

prompt = st.chat_input("Generate Ideas")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.spinner("Generating answer..."):
        answer = ai.step2(atomic_unit, st.session_state.messages)
    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.chat_message("user").write(prompt)
    st.chat_message("assistant").write(answer)