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

st.subheader("Why It Matters")

skill_kernels = app_utils.load_skill_kernels()
benefits = app_utils.load_kernel_benefits() or {}
benefit_mappings = app_utils.load_kernel_benefit_mappings() or []

all_kernels: list[dict] = []
if isinstance(skill_kernels, dict):
    for kern_list in skill_kernels.values():
        if isinstance(kern_list, list):
            all_kernels.extend(kern_list)

for idx, kernel in enumerate(all_kernels, start=1):
    if isinstance(kernel, dict):
        kernel.setdefault("id", f"k{idx}")

benefit_options = list(benefits.values())

if "benefit_inputs" not in st.session_state:
    st.session_state.benefit_inputs = {}
    for kernel in all_kernels:
        existing = [
            benefits[m["benefit_id"]]
            for m in benefit_mappings
            if m.get("kernel_id") == kernel.get("id") and m.get("benefit_id") in benefits
        ]
        st.session_state.benefit_inputs[kernel["id"]] = {
            "selected": existing,
            "new": "",
        }


def suggest_benefits(kern):
    with st.spinner("Generating why it matters..."):
        reasons = ai.step2_why_it_matters(atomic_unit, kern)
    st.session_state.benefit_inputs[kern["id"]]["new"] = "\n".join(reasons)

for kernel in all_kernels:
    st.markdown(f"**{kernel.get('kernel', '')}**")
    st.session_state.benefit_inputs[kernel["id"]]["selected"] = st.multiselect(
        "Select existing benefits",
        benefit_options,
        default=st.session_state.benefit_inputs[kernel["id"]]["selected"],
        key=f"select_{kernel['id']}",
    )
    st.session_state.benefit_inputs[kernel["id"]]["new"] = st.text_area(
        "Add new benefits (one per line, optional '||' for copy override)",
        value=st.session_state.benefit_inputs[kernel["id"]]["new"],
        key=f"new_{kernel['id']}",
        height=80,
    )
    st.button(
        "Generate Why It Matters",
        key=f"gen_{kernel['id']}",
        on_click=lambda k=kernel: suggest_benefits(k),
    )
    st.write("---")

if st.button("Save Why It Matters"):
    benefits_dict = dict(benefits)
    mappings = []
    for kernel in all_kernels:
        selected = st.session_state.benefit_inputs[kernel["id"]]["selected"]
        new_lines = st.session_state.benefit_inputs[kernel["id"]]["new"].splitlines()
        texts = selected + [l.strip() for l in new_lines if l.strip()]
        for text in texts:
            if "||" in text:
                base, override = [p.strip() for p in text.split("||", 1)]
            else:
                base, override = text.strip(), None
            benefit_id = next((bid for bid, val in benefits_dict.items() if val == base), None)
            if benefit_id is None:
                benefit_id = f"w{len(benefits_dict)+1}"
                benefits_dict[benefit_id] = base
            mapping = {"kernel_id": kernel["id"], "benefit_id": benefit_id}
            if override:
                mapping["copy_override"] = override
            mappings.append(mapping)
    app_utils.save_kernel_benefits(json.dumps(benefits_dict))
    app_utils.save_kernel_benefit_mappings(json.dumps(mappings))


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

