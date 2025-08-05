import streamlit as st
import app_utils
import ai

st.header("Step 1 - Atomic unit")
st.info(
    "Practical skills that require bodily control (e.g., horse riding or knife handling) "
    "are not yet supported. These will be implemented in a future version, so please "
    "avoid using them as atomic units."
)

with st.form("step1_form"):

    st.subheader("Learning Types")
    st.checkbox(
        "Declarative (static) – facts, concepts, schemas",
        disabled=True,
        key="lt_declarative",
    )
    st.checkbox(
        "Procedural (dynamic) – algorithms, skills, sequences",
        disabled=True,
        key="lt_procedural",
    )
    st.checkbox(
        "Psychomotor – fine- and gross-motor execution",
        disabled=True,
        key="lt_psychomotor",
    )
    st.checkbox(
        "Metacognitive / Conditional – when & why to deploy 1-3",
        disabled=True,
        key="lt_metacognitive",
    )
    atomic_unit_input = st.text_input(
        "What is the atomic unit that the game should be based on?"
    )
    submitted = st.form_submit_button("Next")

if submitted:
    app_utils.save_atomic_unit(atomic_unit_input)

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    st.chat_message(message["role"]).write(message["content"])

prompt = st.chat_input("Generate Ideas")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.spinner("Generating answer..."):
        answer = ai.step1(st.session_state.messages)
    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.chat_message("user").write(prompt)
    st.chat_message("assistant").write(answer)
