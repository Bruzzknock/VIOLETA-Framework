import streamlit as st
import app_utils
import ai

st.header("Step 6 - Form a Game (FAG)")

layer = app_utils.load_layered_feelings()
if isinstance(layer, dict):
    layer_text = app_utils.layered_feelings_to_text(layer)
else:
    layer_text = layer

mapping = app_utils.load_mechanic_mappings()
if isinstance(mapping, dict):
    mapping_text = app_utils.mechanic_mappings_to_text(mapping)
else:
    mapping_text = mapping

bmt = app_utils.load_base_mechanics_tree()
if isinstance(bmt, dict):
    bmt_text = app_utils.layered_feelings_to_text(bmt)
else:
    bmt_text = bmt

if "medium" not in st.session_state:
    st.session_state.medium = "Video games"
medium = st.radio(
    "Prefer mechanics from:",
    ["Video games", "Board games"],
    index=0 if st.session_state.medium == "Video games" else 1,
)
st.session_state.medium = medium

with st.form("step6_form"):
    st.text_area("Layer Feelings (reference)", layer_text, height=120, disabled=True)
    mechanics_input = st.text_area(
        "Map each feeling to mechanics (Feeling: mechanic1, mechanic2)",
        value=mapping_text,
        height=160,
    )
    submitted = st.form_submit_button("Save Mapping")

if submitted:
    app_utils.save_mechanic_mappings(mechanics_input)
    lf = layer if isinstance(layer, dict) else app_utils._parse_layered_feelings(layer_text)
    mapping_dict = app_utils.load_mechanic_mappings()
    if isinstance(mapping_dict, str):
        mapping_dict = app_utils._parse_mechanic_mappings(mapping_dict)
    bmt_dict = app_utils.build_base_mechanics_tree(lf, mapping_dict)
    bmt_text = app_utils.layered_feelings_to_text(bmt_dict)
    app_utils.save_base_mechanics_tree(bmt_text)

st.subheader("Base Mechanics Tree")
st.text_area("Auto-generated BMT", bmt_text, height=160, disabled=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    st.chat_message(message["role"]).write(message["content"])

prompt = st.chat_input("Generate Ideas")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.spinner("Generating answer..."):
        answer = ai.step6_mechanic_ideas(layer_text, medium, st.session_state.messages)
    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.chat_message("user").write(prompt)
    st.chat_message("assistant").write(answer)
