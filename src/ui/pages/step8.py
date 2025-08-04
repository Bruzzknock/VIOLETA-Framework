import streamlit as st
import pandas as pd
import app_utils
import ai

st.header("Step 8 - Scaling Influence Table (SIT)")

# Load atomic-unit skills
raw_skills = app_utils.load_atomic_skills()
skills: list[str] = []
if isinstance(raw_skills, dict):
    for val in raw_skills.values():
        if isinstance(val, list):
            skills.extend(val)
        else:
            skills.append(str(val))
elif isinstance(raw_skills, list):
    skills = [str(s) for s in raw_skills]
else:
    if raw_skills:
        skills = [str(raw_skills)]

# Load top-level feelings (emotions)
em_arc = app_utils.load_emotional_arc()
feelings = em_arc.get("feelings", {}) if em_arc else {}
emotion_descriptions: dict[str, str] = {}
emotions: list[str] = []
if isinstance(feelings, dict):
    emotion_descriptions = {str(k): str(v) for k, v in feelings.items()}
    emotions = list(emotion_descriptions.keys())
elif isinstance(feelings, list):
    emotions = [str(v) for v in feelings]
elif feelings:
    emotions = [str(feelings)]

# Ensure every emotion has a description key
for emo in emotions:
    emotion_descriptions.setdefault(emo, "")

existing = app_utils.load_sit()
if not isinstance(existing, dict):
    existing = {}

# Build DataFrame with '-' defaults
df = pd.DataFrame('-', index=skills, columns=emotions)
for skill, emos in existing.items():
    if skill in df.index and isinstance(emos, dict):
        for emo, mark in emos.items():
            if emo in df.columns and mark in ['+', '-']:
                df.loc[skill, emo] = mark
    elif skill in df.index and isinstance(emos, list):
        # Backwards compatibility for old list-only format
        for emo in emos:
            if emo in df.columns:
                df.loc[skill, emo] = '+'

with st.form("sit_form"):
    st.write("Toggle '+' if a skill directly influences an emotion.")
    editable = df.reset_index().rename(columns={'index': 'Atomic Unit Skill'})
    config = {
        emo: st.column_config.SelectboxColumn(
            options=['+', '-'],
            help=emotion_descriptions.get(emo, ""),
        )
        for emo in emotions
    }
    edited = st.data_editor(
        editable,
        column_config=config,
        disabled=["Atomic Unit Skill"],
        hide_index=True,
    )
    submitted = st.form_submit_button("Save Table")

if submitted:
    result: dict[str, dict[str, str]] = {}
    for row in edited.to_dict(orient="records"):
        skill = row.get("Atomic Unit Skill")
        result[skill] = {emo: row.get(emo, '-') for emo in emotions}
    app_utils.save_sit(result)
    existing = result
    st.success("SIT saved.")

sit_text = app_utils.sit_to_text(existing) if isinstance(existing, dict) else str(existing)
st.text_area("Current SIT (Skill: emotion +/-)", sit_text, height=160)

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    st.chat_message(message["role"]).write(message["content"])

prompt = st.chat_input("Generate Ideas")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.spinner("Generating answer..."):
        answer = ai.step8_sit_ideas(skills, emotions, st.session_state.messages)
    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.chat_message("user").write(prompt)
    st.chat_message("assistant").write(answer)
