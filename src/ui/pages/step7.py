import streamlit as st
import app_utils
import ai

st.header("Step 7 - Build the MVP")

bmt = app_utils.load_base_mechanics_tree()
if isinstance(bmt, dict):
    bmt_text = app_utils.layered_feelings_to_text(bmt)
else:
    bmt_text = bmt

schemas = app_utils.load_list_of_schemas()
if isinstance(schemas, list):
    schemas_text = app_utils.schemas_to_text(schemas)
else:
    schemas_text = schemas

with st.form("step7_form"):
    st.text_area("Base Mechanics Tree (reference)", bmt_text, height=160, disabled=True)
    schemas_input = st.text_area(
        "List of Schemas (name: property)", value=schemas_text, height=160
    )
    submitted = st.form_submit_button("Save Schemas")

if submitted:
    app_utils.save_list_of_schemas(schemas_input)

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    st.chat_message(message["role"]).write(message["content"])

prompt = st.chat_input("Generate Ideas")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.spinner("Generating answer..."):
        answer = ai.step7_mvp_ideas(bmt_text, st.session_state.messages)
    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.chat_message("user").write(prompt)
    st.chat_message("assistant").write(answer)
