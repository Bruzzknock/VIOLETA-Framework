import streamlit as st
import pandas as pd
import app_utils
import ai

st.header("Step 8B - Triadic Integration Table (TIT)")

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
skills = emotion_skills.get(emotion, [])

schemas = app_utils.get_schemas_for_emotion(emotion)

existing_tit = app_utils.load_tit()
if not isinstance(existing_tit, dict):
    existing_tit = {}
emotion_table = existing_tit.get(emotion, {})

# Build initial DataFrame
rows = []
for schema in schemas:
    row = {"Schema": schema}
    for sk in skills:
        cell_val = emotion_table.get(schema, {}).get(sk, "")
        if isinstance(cell_val, bool):
            cell_val = "✔" if cell_val else ""
        row[sk] = cell_val
    row["Result"] = emotion_table.get(schema, {}).get("Result", "")
    rows.append(row)

df = pd.DataFrame(rows)

if "tit_df" not in st.session_state:
    st.session_state.tit_df = df

def generate_suggestions():
    with st.spinner("Generating suggestions..."):
        for schema in schemas:
            mask = st.session_state.tit_df["Schema"] == schema
            for sk in skills:
                suggestion = ai.step8b_cell(schema, sk, emotion)
                st.session_state.tit_df.loc[mask, sk] = suggestion

st.button("Suggest Explanations", on_click=generate_suggestions)

with st.form("tit_form"):
    config = {sk: st.column_config.TextColumn() for sk in skills}
    edited = st.data_editor(
        st.session_state.tit_df,
        column_config=config,
        disabled=["Schema"],
        hide_index=True,
    )
    submitted = st.form_submit_button("Save TIT")

if submitted:
    result: dict[str, dict[str, object]] = {}
    for row in edited.to_dict(orient="records"):
        schema = row.get("Schema")
        result[schema] = {sk: row.get(sk, "") for sk in skills}
        result[schema]["Result"] = row.get("Result", "")
    existing_tit[emotion] = result
    app_utils.save_tit(existing_tit)
    st.session_state.tit_df = edited
    st.success("TIT saved.")

# Display current TIT as text for reference
current = existing_tit.get(emotion, {})
lines = []
for schema, vals in current.items():
    entries = [f"{sk}: {vals.get(sk, '')}" for sk in skills]
    entries.append(f"Result: {vals.get('Result', '')}")
    lines.append(f"{schema} | " + ", ".join(entries))

tit_text = "\n".join(lines)
st.text_area("Current TIT", tit_text, height=200)
