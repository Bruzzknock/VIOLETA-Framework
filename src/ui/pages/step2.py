import json
import streamlit as st
import app_utils
import ai

st.header("Step 2 - Atomic Skills & Kernels")

atomic_unit = app_utils.load_atomic_unit()
learning_types = app_utils.load_learning_types()
if not learning_types:
    learning_types = ["declarative", "procedural", "metacognitive"]

loaded_skills = app_utils.load_atomic_skills()
skills_text_default = app_utils.atomic_skills_to_text(loaded_skills)


def _type_map(skills) -> dict[str, str]:
    mapping: dict[str, str] = {}
    if isinstance(skills, dict):
        for items in skills.values():
            if isinstance(items, list):
                for item in items:
                    if isinstance(item, dict):
                        mapping[item.get("name", "")] = item.get("type", "")
                    else:
                        mapping[str(item)] = ""
            elif isinstance(items, dict):
                mapping[items.get("name", "")] = items.get("type", "")
            else:
                mapping[str(items)] = ""
    elif isinstance(skills, list):
        for item in skills:
            if isinstance(item, dict):
                mapping[item.get("name", "")] = item.get("type", "")
            else:
                mapping[str(item)] = ""
    return mapping


existing_types = _type_map(loaded_skills)


with st.form("step2_form"):
    atomic_skills_input = st.text_area(
        "What knowledge, actions, and/or skills are necessary to master this atomic unit?\n\n"
        "You can group skills by entering a category name followed by its skills on separate lines.\n"
        "Leave a blank line between categories.",
        value=skills_text_default,
        height=200,
    )
    parsed_skills = app_utils._parse_atomic_skills(atomic_skills_input)
    flat_skills = app_utils.skill_names(parsed_skills)
    key_map: dict[str, str] = {}
    for i, skill in enumerate(flat_skills):
        key = f"lt_{i}"
        key_map[skill] = key
        current = existing_types.get(skill, learning_types[0] if learning_types else "")
        idx = learning_types.index(current) if current in learning_types else 0
        st.selectbox(f"{skill} learning type", learning_types, index=idx, key=key)
    submitted = st.form_submit_button("Next")

if submitted:
    if isinstance(parsed_skills, dict):
        structured = {}
        for cat, names in parsed_skills.items():
            structured[cat] = []
            for name in names:
                lt = st.session_state.get(key_map.get(name, ""), "")
                structured[cat].append({"name": name, "type": lt})
    else:
        structured = []
        for name in flat_skills:
            lt = st.session_state.get(key_map.get(name, ""), "")
            structured.append({"name": name, "type": lt})
    app_utils.save_atomic_skills(structured)

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
