import streamlit as st
import pandas as pd
import app_utils
import ai

st.header("Step 8B - Triadic Integration Table – Kernel (TIT-K)")

# Load SIT to find skill-emotion '+' pairs
sit = app_utils.load_sit()
if not isinstance(sit, dict):
    sit = {}

emotion_skills: dict[str, list[str]] = {}
for skill, emos in sit.items():
    if isinstance(emos, dict):
        for emo, mark in emos.items():
            if mark == '+':
                emotion_skills.setdefault(emo, []).append(skill)

if not emotion_skills:
    st.info("No skill-emotion '+' pairs found in SIT.")
    st.stop()

emotion = st.selectbox("Select Emotion", sorted(emotion_skills.keys()))
skill = st.selectbox("Select Skill", sorted(emotion_skills.get(emotion, [])))

mechanics = app_utils.get_schemas_for_emotion(emotion)

skill_kernels = app_utils.load_skill_kernels()
kernel_list = skill_kernels.get(skill, []) if isinstance(skill_kernels, dict) else []

existing_tit = app_utils.load_tit()
if not isinstance(existing_tit, dict):
    existing_tit = {}
skill_table = existing_tit.get(emotion, {}).get(skill, {})

# Build initial DataFrame
kernel_map: dict[str, str] = {}
rows = []
for idx, kernel_info in enumerate(kernel_list, start=1):
    kernel_text = kernel_info.get("kernel", "") if isinstance(kernel_info, dict) else str(kernel_info)
    label = f"K_{idx} {kernel_text}"
    kernel_map[label] = kernel_text
    row = {"Kernel": label}
    for mech in mechanics:
        cell_val = skill_table.get(label, {}).get(mech, "")
        if isinstance(cell_val, bool):
            cell_val = "✔" if cell_val else ""
        row[mech] = cell_val
    row["Result"] = skill_table.get(label, {}).get("Result", "")
    rows.append(row)

df = pd.DataFrame(rows)

# Reset the table whenever a different emotion or skill is selected
if (
    st.session_state.get("tit_emotion") != emotion
    or st.session_state.get("tit_skill") != skill
):
    st.session_state.tit_emotion = emotion
    st.session_state.tit_skill = skill
    st.session_state.tit_df = df


def generate_suggestions():
    with st.spinner("Generating suggestions..."):
        for label, kernel_text in kernel_map.items():
            mask = st.session_state.tit_df["Kernel"] == label
            for mech in mechanics:
                suggestion = ai.step8b_cell(kernel_text, mech, emotion)
                st.session_state.tit_df.loc[mask, mech] = suggestion


st.button("Evaluate Pairings", on_click=generate_suggestions)

with st.form("tit_form"):
    config = {mech: st.column_config.TextColumn() for mech in mechanics}
    edited = st.data_editor(
        st.session_state.tit_df,
        column_config=config,
        disabled=["Kernel"],
        hide_index=True,
    )
    submitted = st.form_submit_button("Save TIT-K")

if submitted:
    result: dict[str, dict[str, object]] = {}
    for row in edited.to_dict(orient="records"):
        label = row.get("Kernel")
        result[label] = {mech: row.get(mech, "") for mech in mechanics}
        result[label]["Result"] = row.get("Result", "")
    existing_tit.setdefault(emotion, {})[skill] = result
    app_utils.save_tit(existing_tit)
    st.session_state.tit_df = edited
    st.success("TIT-K saved.")

# Display current TIT-K as text for reference
current = existing_tit.get(emotion, {}).get(skill, {})
lines = []
for label, vals in current.items():
    entries = [f"{mech}: {vals.get(mech, '')}" for mech in mechanics]
    entries.append(f"Result: {vals.get('Result', '')}")
    lines.append(f"{label} | " + ", ".join(entries))

tit_text = "\n".join(lines)
st.text_area("Current TIT-K", tit_text, height=200)
