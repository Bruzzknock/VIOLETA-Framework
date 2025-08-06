import json
import streamlit as st
import app_utils
import ai

st.header("Step 2 - Atomic Skills & Kernels")

atomic_unit = app_utils.load_atomic_unit()
learning_types = app_utils.load_learning_types()
loaded_skills = app_utils.load_atomic_skills()

# Display selected learning types
if learning_types:
    st.write("Learning Types: " + ", ".join(learning_types))

st.write(
    "What knowledge, actions, and/or skills are necessary to master this atomic unit?"
)

# Ensure session state for skill inputs exists and is pre-populated
if "skill_inputs" not in st.session_state:
    st.session_state.skill_inputs = {}
if isinstance(loaded_skills, dict):
    for lt in learning_types:
        st.session_state.skill_inputs.setdefault(
            lt, "\n".join(loaded_skills.get(lt, []))
        )
else:
    for lt in learning_types:
        st.session_state.skill_inputs.setdefault(lt, "")

with st.form("step2_form"):
    for lt in learning_types:
        st.session_state.skill_inputs[lt] = st.text_area(
            f"{lt} Skills",
            value=st.session_state.skill_inputs.get(lt, ""),
            height=120,
            key=f"skill_{lt}",
        )
    submitted = st.form_submit_button("Next")

if submitted:
    parsed = {
        lt: [
            s.strip()
            for s in st.session_state.skill_inputs.get(lt, "").splitlines()
            if s.strip()
        ]
        for lt in learning_types
    }
    app_utils.save_atomic_skills(parsed)

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

