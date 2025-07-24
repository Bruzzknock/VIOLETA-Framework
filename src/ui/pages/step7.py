import streamlit as st
import app_utils
import ai


def _rerun():
    """Trigger a Streamlit rerun compatible across versions."""
    if hasattr(st, "rerun"):
        st.rerun()
    else:
        st.experimental_rerun()

st.header("Step 7 - Build the MVP")

# medium preference saved from Step 6
medium = st.session_state.get("medium", "Video games")

# ---------------------------------------------------------------------------
# Load data
bmt = app_utils.load_base_mechanics_tree()
if isinstance(bmt, dict):
    bmt_text = app_utils.layered_feelings_to_text(bmt)
    root_mechanics = list(bmt.keys())
else:
    bmt_text = str(bmt)
    root_mechanics = []

saved_queue = app_utils.load_step7_queue()

existing = app_utils.load_list_of_schemas()
if isinstance(existing, list):
    schemas_text = app_utils.schemas_to_text(existing)
    initial_schemas = existing
else:
    schemas_text = str(existing)
    initial_schemas = []

# Load theme vignette and kernel mappings for theme-fit assistance
vignette = app_utils.load_emotional_arc().get("vignette", "")
kernel_mappings = app_utils.load_kernel_theme_mapping()

# ---------------------------------------------------------------------------
# Manual edit of the final List of Schemas
with st.form("step7_form"):
    st.text_area("Base Mechanics Tree (reference)", bmt_text, height=160, disabled=True)
    schemas_input = st.text_area(
        "List of Schemas (name: property)", value=schemas_text, height=160
    )
    submitted = st.form_submit_button("Save Schemas")

if submitted:
    app_utils.save_list_of_schemas(schemas_input)

# ---------------------------------------------------------------------------
# Recursive workflow state management
if "rec_queue" not in st.session_state:
    if saved_queue:
        st.session_state.rec_queue = list(saved_queue)
    else:
        processed = {item.get("name") for item in initial_schemas}
        st.session_state.rec_queue = [m for m in root_mechanics if m not in processed]
    st.session_state.current = None
    st.session_state.stage = None
    st.session_state.new_elements = []
    st.session_state.schemas = list(initial_schemas)
    app_utils.save_step7_queue(st.session_state.rec_queue)

if st.button("Reset Recursive Workflow"):
    processed = {item.get("name") for item in initial_schemas}
    st.session_state.rec_queue = [m for m in root_mechanics if m not in processed]
    st.session_state.current = None
    st.session_state.stage = None
    st.session_state.new_elements = []
    st.session_state.schemas = list(initial_schemas)
    app_utils.save_step7_queue(st.session_state.rec_queue)
    _rerun()

# ---------------------------------------------------------------------------
# Recursive data entry
if st.session_state.rec_queue or st.session_state.stage:
    if st.session_state.current is None:
        st.session_state.current = st.session_state.rec_queue.pop(0)
        app_utils.save_step7_queue(st.session_state.rec_queue)
        st.session_state.stage = "decompose"
        # reset chat messages for the new mechanic
        st.session_state.messages = []

    mech = st.session_state.current
    st.subheader(f"Break down: {mech}")

    if st.session_state.stage == "decompose":
        with st.form("decompose_form"):
            elements_text = st.text_area(
                "Which concrete game elements does this mechanic consist of?",
                key="elements_input",
            )
            submitted = st.form_submit_button("Next")
            done = st.form_submit_button("Done")
        if submitted:
            elements = [e.strip() for e in elements_text.splitlines() if e.strip()]
            st.session_state.new_elements = elements
            st.session_state.stage = "theme"
            st.session_state.messages = []  # reset chat for theme fit
            _rerun()
        elif done:
            st.session_state.schemas.append({"name": mech, "property": ""})
            app_utils.save_list_of_schemas(app_utils.schemas_to_text(st.session_state.schemas))
            app_utils.save_step7_queue(st.session_state.rec_queue)
            st.session_state.current = None
            st.session_state.stage = None
            st.session_state.new_elements = []
            st.session_state.messages = []
            _rerun()

    elif st.session_state.stage == "theme":
        st.markdown("**For each element, describe its thematic meaning and function.**")
        with st.form("theme_form"):
            inputs = {}
            for el in st.session_state.new_elements:
                inputs[el] = st.text_input(el, key=f"theme_{el}")
            save = st.form_submit_button("Save Element")
        if save:
            for el in st.session_state.new_elements:
                prop = st.session_state.get(f"theme_{el}", "")
                st.session_state.schemas.append({"name": el, "property": prop})
                st.session_state.rec_queue.append(el)
            app_utils.save_list_of_schemas(app_utils.schemas_to_text(st.session_state.schemas))
            app_utils.save_step7_queue(st.session_state.rec_queue)
            st.session_state.current = None
            st.session_state.stage = None
            st.session_state.new_elements = []
            st.session_state.messages = []  # reset chat after element saved
            _rerun()

else:
    st.success("All mechanics processed.")
    schemas_display = app_utils.schemas_to_text(st.session_state.schemas)
    st.text_area("Resulting List of Schemas", schemas_display, height=160)
    if st.button("Save Result"):
        app_utils.save_list_of_schemas(schemas_display)
        app_utils.save_step7_queue([])
        st.success("Schemas saved.")

# ---------------------------------------------------------------------------
# Chat assistant
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    st.chat_message(message["role"]).write(message["content"])

prompt = st.chat_input("Generate Ideas")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.spinner("Generating answer..."):
        if st.session_state.get("stage") == "theme":
            parent = st.session_state.get("current", "")
            element = ", ".join(st.session_state.get("new_elements", []))
            answer = ai.step7_theme_fit(
                vignette,
                kernel_mappings,
                parent,
                element,
                st.session_state.messages,
            )
        else:
            mech = st.session_state.get("current", "") or bmt_text
            answer = ai.step7_mvp_ideas(mech, medium, st.session_state.messages)
    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.chat_message("user").write(prompt)
    st.chat_message("assistant").write(answer)
