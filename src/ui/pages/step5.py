import streamlit as st
import app_utils
import ai

st.header("Step 5 - Layer Feelings (LF) Process")

emotional_arc = app_utils.load_emotional_arc()
feelings = emotional_arc.get("feelings", "") if emotional_arc else ""

layer_default = app_utils.load_layered_feelings()

with st.form("step5_form"):
    layer_input = st.text_area(
        "Arrange the feelings into a hierarchy or sequence:",
        value=layer_default,
        height=120,
    )
    submitted = st.form_submit_button("Save Layered Feelings")

if submitted:
    app_utils.save_layered_feelings(layer_input)

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    st.chat_message(message["role"]).write(message["content"])

prompt = st.chat_input("Generate Ideas")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.spinner("Generating answer..."):
        answer = ai.step5(feelings, st.session_state.messages)
    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.chat_message("user").write(prompt)
    st.chat_message("assistant").write(answer)

