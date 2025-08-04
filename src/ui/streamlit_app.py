import streamlit as st
import app_utils
import ai

st.set_page_config(page_title="VIOLETA Wizard", layout="wide")
st.title("🎮 VIOLETA Framework Wizard")
st.sidebar.success("Select a step above.")

if st.sidebar.button(
    "Generate Game Description",
    disabled=not app_utils.all_steps_completed(),
):
    info = app_utils.load_all_sections()
    with st.spinner("Generating description..."):
        description = ai.generate_game_description(info)
    st.session_state["game_description"] = description

if "game_description" in st.session_state:
    st.subheader("Game Description")
    st.write(st.session_state["game_description"])
