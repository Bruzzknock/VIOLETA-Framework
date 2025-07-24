import streamlit as st
import app_utils
import ai


def _rerun():
    """Trigger a Streamlit rerun compatible across versions."""
    if hasattr(st, "rerun"):
        st.rerun()
    else:
        st.experimental_rerun()


def _save_queue(include_current: bool = False) -> None:
    """Persist the current queue, optionally including the active item."""
    queue = list(st.session_state.rec_queue)
    if include_current and st.session_state.get("current") is not None:
        queue = [
            {
                "name": st.session_state.current,
                "parent": st.session_state.parent,
                "stage": st.session_state.stage or "decompose",
            }
        ] + queue
    app_utils.save_step7_queue(queue)

st.header("Step 7 - Build the MVP")

# medium preference saved from Step 6
medium = st.session_state.get("medium", "Video games")

# ---------------------------------------------------------------------------
# Load data
bmt = app_utils.load_base_mechanics_tree()
if isinstance(bmt, dict):
    bmt_text = app_utils.layered_feelings_to_text(bmt)
    root_mechanics = app_utils.flatten_mechanics(bmt)
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
        converted = []
        for item in saved_queue:
            if isinstance(item, dict):
                converted.append(item)
            elif isinstance(item, list):
                if len(item) == 3:
                    name, parent, stage = item
                    converted.append({"name": name, "parent": parent, "stage": stage})
                elif len(item) == 2:
                    name, parent = item
                    converted.append({"name": name, "parent": parent, "stage": "decompose"})
            else:
                converted.append({"name": str(item), "parent": "", "stage": "decompose"})
        st.session_state.rec_queue = converted
    else:
        processed = {item.get("name") for item in initial_schemas}
        st.session_state.rec_queue = [
            {"name": m, "parent": "", "stage": "decompose"}
            for m in root_mechanics
            if m not in processed
        ]
    st.session_state.current = None
    st.session_state.parent = ""
    st.session_state.stage = None
    st.session_state.schemas = list(initial_schemas)
    _save_queue()

if st.button("Reset Recursive Workflow"):
    processed = {item.get("name") for item in initial_schemas}
    st.session_state.rec_queue = [
        {"name": m, "parent": "", "stage": "decompose"}
        for m in root_mechanics
        if m not in processed
    ]
    st.session_state.current = None
    st.session_state.parent = ""
    st.session_state.stage = None
    st.session_state.schemas = list(initial_schemas)
    _save_queue()
    _rerun()

# ---------------------------------------------------------------------------
# Recursive data entry
if st.session_state.rec_queue or st.session_state.stage:
    if st.session_state.current is None:
        item = st.session_state.rec_queue.pop(0)
        if isinstance(item, dict):
            st.session_state.current = item.get("name")
            st.session_state.parent = item.get("parent", "")
            st.session_state.stage = item.get("stage", "decompose")
        else:
            st.session_state.current = item[0]
            st.session_state.parent = item[1] if len(item) > 1 else ""
            st.session_state.stage = "decompose"
        _save_queue(include_current=True)
        st.session_state.messages = []

    mech = st.session_state.current
    st.subheader(f"Break down: {mech}")

    if st.session_state.stage == "decompose":
        with st.form("decompose_form"):
            elements_text = st.text_area(
                "List elements for this mechanic (Name: description)",
                key="elements_input",
            )
            submitted = st.form_submit_button("Next")
            done = st.form_submit_button("Done")
        if submitted:
            parsed = []
            for line in elements_text.splitlines():
                line = line.strip()
                if not line:
                    continue
                if ":" in line:
                    name, _ = line.split(":", 1)
                    parsed.append({"name": name.strip(), "parent": mech, "stage": "decompose"})
                else:
                    parsed.append({"name": line, "parent": mech, "stage": "decompose"})
            if parsed:
                st.session_state.rec_queue = (
                    [
                        {
                            "name": mech,
                            "parent": st.session_state.parent,
                            "stage": "theme",
                        }
                    ]
                    + parsed
                    + st.session_state.rec_queue
                )
                _save_queue()
                st.session_state.current = None
                st.session_state.parent = ""
                st.session_state.stage = None
                st.session_state.messages = []
                _rerun()
            else:
                st.session_state.stage = "theme"
                st.session_state.messages = []
                _rerun()
        elif done:
            st.session_state.stage = "theme"
            st.session_state.messages = []
            _rerun()

    elif st.session_state.stage == "theme":
        with st.form("theme_form"):
            prop = st.text_area("Thematic function", key="theme_input")
            save = st.form_submit_button("Save Element")
        if save:
            st.session_state.schemas.append({"name": mech, "property": prop})
            app_utils.save_list_of_schemas(
                app_utils.schemas_to_text(st.session_state.schemas)
            )
            _save_queue()
            st.session_state.current = None
            st.session_state.parent = ""
            st.session_state.stage = None
            st.session_state.messages = []
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
            parent = st.session_state.get("parent", "")
            element = st.session_state.get("current", "")
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
