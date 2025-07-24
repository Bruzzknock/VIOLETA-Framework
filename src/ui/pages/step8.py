import json
import streamlit as st
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
emotions: list[str] = []
if isinstance(feelings, dict):
    emotions = [str(v) for v in feelings.values()]
elif isinstance(feelings, list):
    emotions = [str(v) for v in feelings]
elif feelings:
    emotions = [str(feelings)]

# Load existing SIT
def _ensure_dict(data):
    if isinstance(data, dict):
        return data
    try:
        return json.loads(data)
    except Exception:
        return {}

existing = _ensure_dict(app_utils.load_sit())

with st.form("sit_form"):
    st.write("Mark a '+' for each direct skill → emotion influence.")
    selections = {}
    for skill in skills:
        cols = st.columns(len(emotions) + 1)
        cols[0].markdown(f"**{skill}**")
        for idx, emo in enumerate(emotions):
            key = f"{skill}_{emo}"
            checked = emo in existing.get(skill, [])
            selections[key] = cols[idx + 1].checkbox("", value=checked, key=key)
    submitted = st.form_submit_button("Save Table")

if submitted:
    result = {}
    for skill in skills:
        marked = []
        for emo in emotions:
            key = f"{skill}_{emo}"
            if st.session_state.get(key):
                marked.append(emo)
        if marked:
            result[skill] = marked
    app_utils.save_sit(json.dumps(result))
    existing = result
    st.success("SIT saved.")

sit_text = app_utils.sit_to_text(existing) if isinstance(existing, dict) else str(existing)
st.text_area("Current SIT (Skill: emotion list)", sit_text, height=160)

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
