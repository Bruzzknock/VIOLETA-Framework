import streamlit as st
import app_utils
import ai

st.header("Step 1 - Atomic unit")
st.info(
    "Practical skills that require bodily control (e.g., horse riding or knife handling) "
    "are not yet supported. These will be implemented in a future version, so please "
    "avoid using them as atomic units."
)

saved_types = set(app_utils.load_learning_types())
saved_atomic_unit = app_utils.load_atomic_unit()

with st.form("step1_form"):

    st.subheader("Learning Types")
    lt_declarative = st.checkbox(
        "Declarative (static) – facts, concepts, schemas",
        key="lt_declarative",
        value="Declarative" in saved_types,
    )
    lt_procedural = st.checkbox(
        "Procedural (dynamic) – algorithms, skills, sequences",
        key="lt_procedural",
        value="Procedural" in saved_types,
    )
    st.checkbox(
        "Psychomotor – fine- and gross-motor execution",
        disabled=True,
        value="Psychomotor" in saved_types,
    )
    lt_metacognitive = st.checkbox(
        "Metacognitive / Conditional – when & why to deploy 1-3",
        key="lt_metacognitive",
        value="Metacognitive" in saved_types,
    )
    atomic_unit_input = st.text_input(
        "What is the atomic unit that the game should be based on?",
        value=saved_atomic_unit,
    )
    submitted = st.form_submit_button("Next")

if submitted:
    selected_types = []
    if lt_declarative:
        selected_types.append("Declarative")
    if lt_procedural:
        selected_types.append("Procedural")
    if lt_metacognitive:
        selected_types.append("Metacognitive")
    app_utils.save_learning_types(selected_types)
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
