import json
import streamlit as st
import re
import app_utils
import ai

st.header("Step 2 - Atomic Skills & Kernels")

atomic_unit = app_utils.load_atomic_unit()
learning_types = app_utils.load_learning_types()
if not learning_types:
    learning_types = ["declarative", "procedural", "metacognitive"]

loaded_skills = app_utils.load_atomic_skills()
skills_text_default = app_utils.atomic_skills_to_text(loaded_skills)

with st.form("step2_form"):
    atomic_skills_input = st.text_area(
        "What knowledge, actions, and/or skills are necessary to master this atomic unit?\n\n"
        "You can group skills by entering a category name followed by its skills on separate lines.\n"
        "Leave a blank line between categories.",
        value=skills_text_default,
        height=200,
    )
    parsed_skills = app_utils._parse_atomic_skills(atomic_skills_input)
    submitted = st.form_submit_button("Next")

if submitted:
    app_utils.save_atomic_skills(parsed_skills)

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


def _kernel_key(skill: str, idx: int) -> str:
    safe = re.sub(r"\W+", "_", skill)
    return f"lt_{safe}_{idx}"


kernel_data = {}
try:
    kernel_data = json.loads(st.session_state.kernels_text)
except Exception:
    kernel_data = {}

for skill, kernel_list in kernel_data.items():
    st.markdown(f"**{skill}**")
    for idx, kernel_info in enumerate(kernel_list):
        kernel_sentence = (
            kernel_info.get("kernel", "") if isinstance(kernel_info, dict) else str(kernel_info)
        )
        key = _kernel_key(skill, idx)
        current = kernel_info.get("type", "") if isinstance(kernel_info, dict) else ""
        sel_idx = learning_types.index(current) if current in learning_types else 0
        color = "green" if isinstance(kernel_info, dict) and kernel_info.get("updated") else "inherit"
        st.markdown(
            f"<span style='color:{color}'>{kernel_sentence}</span>",
            unsafe_allow_html=True,
        )
        st.selectbox(
            "Learning type",
            learning_types,
            index=sel_idx,
            key=key,
        )

def generate_kernels():
    with st.spinner("Generating kernels..."):
        generated = ai.step2_kernels(
            atomic_unit, app_utils.load_atomic_skills()
        )
    st.session_state.kernels_text = generated


def save_kernels():
    try:
        data = json.loads(st.session_state.kernels_text)
    except Exception:
        st.error("Kernels text is not valid JSON")
        return
    for skill, kernel_list in data.items():
        for idx, kernel_info in enumerate(kernel_list):
            lt = st.session_state.get(_kernel_key(skill, idx), "")
            if isinstance(kernel_info, dict):
                kernel_info["type"] = lt
                kernel_info.pop("updated", None)
            else:
                kernel_list[idx] = {"kernel": str(kernel_info), "type": lt}
    app_utils.save_skill_kernels(json.dumps(data))


def adapt_kernels():
    try:
        data = json.loads(st.session_state.kernels_text)
    except Exception:
        st.error("Kernels text is not valid JSON")
        return
    for skill, kernel_list in data.items():
        for idx, kernel_info in enumerate(kernel_list):
            lt = st.session_state.get(_kernel_key(skill, idx), "")
            if isinstance(kernel_info, dict):
                kernel_info["type"] = lt
            else:
                kernel_list[idx] = {"kernel": str(kernel_info), "type": lt}
    with st.spinner("Checking kernels..."):
        to_update_json = ai.kernels_to_update(data)
    try:
        to_update = json.loads(to_update_json)
    except Exception:
        st.error("LLM response was not valid JSON")
        return
    subset = {}
    for skill, idx_list in to_update.items():
        if skill in data:
            selected = []
            for idx in idx_list:
                if isinstance(idx, int) and idx < len(data[skill]):
                    selected.append(data[skill][idx])
            if selected:
                subset[skill] = selected
    if not subset:
        st.info("No kernels require updating.")
        return
    with st.spinner("Updating kernels..."):
        updated_json = ai.update_kernels(subset)
    try:
        new_data = json.loads(updated_json)
    except Exception:
        st.error("LLM response was not valid JSON")
        return
    for skill, idx_list in to_update.items():
        updated_list = new_data.get(skill, [])
        for pos, idx in enumerate(idx_list):
            if skill not in data or idx >= len(data[skill]):
                continue
            old_entry = data[skill][idx]
            old_kernel = ""
            old_type = ""
            if isinstance(old_entry, dict):
                old_kernel = old_entry.get("kernel", "")
                old_type = old_entry.get("type", "")
            updated_entry = updated_list[pos] if pos < len(updated_list) else old_entry
            if isinstance(updated_entry, dict):
                updated_entry.setdefault("type", old_type)
                if updated_entry.get("kernel", "") != old_kernel:
                    updated_entry["updated"] = True
            else:
                new_sentence = str(updated_entry)
                changed = new_sentence != old_kernel
                updated_entry = {"kernel": new_sentence, "type": old_type}
                if changed:
                    updated_entry["updated"] = True
            data[skill][idx] = updated_entry
    st.session_state.kernels_text = json.dumps(data, indent=2)


st.button("Generate Kernels", on_click=generate_kernels)
st.button("Update Kernels", on_click=adapt_kernels)
st.button("Save Kernels", on_click=save_kernels)

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
