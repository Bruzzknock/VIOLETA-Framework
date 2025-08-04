import json
import re
from pathlib import Path

from gdsf import GDSFParser

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = BASE_DIR / "ui" / "data"
DATA_PATH.mkdir(exist_ok=True)
GDSF_FILE = DATA_PATH / "info.gdsf"


def _load_data() -> dict:
    if GDSF_FILE.exists():
        parser = GDSFParser(GDSF_FILE)
        return parser.sections
    return {}


def _save_data(sections: dict) -> None:
    with open(GDSF_FILE, "w") as f:
        for name, values in sections.items():
            f.write(f"[{name}]\n")
            for k, v in values.items():
                f.write(f'{k} = "{v}"\n')
            f.write("\n")


REQUIRED_SECTIONS = [
    "atomic_unit",
    "atomic_skills",
    "skill_kernels",
    "theme",
    "theme_name",
    "kernel_theme_mapping",
    "emotional_arc",
    "layered_feelings",
    "mechanic_mappings",
    "base_mechanics_tree",
    "list_of_schemas",
    "sit_table",
    "tit_table",
]


def load_all_sections() -> dict:
    """Return all sections stored in the gdsf file."""
    return _load_data()


def all_steps_completed() -> bool:
    #TODO
    return True


def save_atomic_unit(value: str) -> None:
    data = _load_data()
    data["atomic_unit"] = {"value": value}
    _save_data(data)


def load_atomic_unit() -> str:
    data = _load_data()
    return data.get("atomic_unit", {}).get("value", "")


def save_learning_types(types: list[str]) -> None:
    data = _load_data()
    data["learning_types"] = {"value": json.dumps(types)}
    _save_data(data)


def load_learning_types() -> list[str]:
    data = _load_data()
    raw = data.get("learning_types", {}).get("value", "[]")
    try:
        return json.loads(raw)
    except Exception:
        return []


def _parse_atomic_skills(text: str):
    """Parse user input for atomic skills.

    Input may contain categories separated by blank lines. The first
    non-empty line after a blank line is treated as a new category. If no
    blank lines are present, all lines are returned as a simple list."""

    lines = [line.strip() for line in text.splitlines()]
    lines = [l for l in lines if l is not None]  # just keep list

    # filter leading/trailing empty lines
    while lines and lines[0] == "":
        lines.pop(0)
    while lines and lines[-1] == "":
        lines.pop()

    if not lines:
        return []

    has_blank = any(line == "" for line in lines)
    if not has_blank:
        # No blank lines -> treat all as skill list
        return [line for line in lines]

    skills = {}
    current = None
    for line in lines:
        if line == "":
            current = None
            continue
        if current is None:
            current = line
            skills[current] = []
        else:
            skills[current].append(line)
    return skills


def save_atomic_skills(skills: str) -> None:
    parsed = _parse_atomic_skills(skills)
    data = _load_data()
    data["atomic_skills"] = {"value": json.dumps(parsed)}
    _save_data(data)


def load_atomic_skills():
    data = _load_data()
    raw = data.get("atomic_skills", {}).get("value", "")
    try:
        return json.loads(raw)
    except Exception:
        return raw


def save_theme(theme: str) -> None:
    data = _load_data()
    data["theme"] = {"value": theme}
    _save_data(data)


def load_theme() -> str:
    data = _load_data()
    return data.get("theme", {}).get("value", "")


def save_theme_name(name: str) -> None:
    data = _load_data()
    data["theme_name"] = {"value": name}
    _save_data(data)


def load_theme_name() -> str:
    data = _load_data()
    return data.get("theme_name", {}).get("value", "")


def save_skill_kernels(kernels: str) -> None:
    """Save skill kernels JSON or raw string to the gdsf file."""
    try:
        parsed = json.loads(kernels)
    except Exception:
        parsed = kernels
    data = _load_data()
    data["skill_kernels"] = {"value": json.dumps(parsed)}
    _save_data(data)


def load_skill_kernels():
    data = _load_data()
    raw = data.get("skill_kernels", {}).get("value", "")
    try:
        return json.loads(raw)
    except Exception:
        return raw


# Adding new kernel mapping functions


def save_kernel_mappings(mappings: str) -> None:
    """Save kernel mapping table to the gdsf file."""
    try:
        parsed = json.loads(mappings)
    except Exception:
        parsed = mappings
    data = _load_data()
    data["kernel_mappings"] = {"value": json.dumps(parsed)}
    _save_data(data)


def load_kernel_mappings():
    data = _load_data()
    raw = data.get("kernel_mappings", {}).get("value", "")
    try:
        return json.loads(raw)
    except Exception:
        return raw


# Functions for saving the kernel-theme mapping produced in Step 3B
def save_kernel_theme_mapping(info: str) -> None:
    """Save Step 3B table to the gdsf file."""
    try:
        parsed = json.loads(info)
    except Exception:
        parsed = info
    data = _load_data()
    data["kernel_theme_mapping"] = {"value": json.dumps(parsed)}
    _save_data(data)


def load_kernel_theme_mapping():
    data = _load_data()
    raw = data.get("kernel_theme_mapping", {}).get("value", "")
    try:
        return json.loads(raw)
    except Exception:
        return raw


# ---------------------------------------------------------------------------
# Step 4: Emotional Arc helpers


def _parse_feelings(feelings: str) -> dict:
    """Convert user input into a dictionary of feelings."""
    try:
        parsed = json.loads(feelings)
        if isinstance(parsed, dict):
            return parsed
        if isinstance(parsed, list):
            return {str(i + 1): item for i, item in enumerate(parsed)}
    except Exception:
        pass

    result: dict[str, str] = {}
    for line in feelings.splitlines():
        line = line.strip()
        if not line:
            continue
        if ":" in line:
            key, value = line.split(":", 1)
            result[key.strip()] = value.strip()
        else:
            result[str(len(result) + 1)] = line
    return result


def feelings_to_text(feelings: dict | list | str) -> str:
    """Convert a feelings structure back into readable text."""
    if isinstance(feelings, dict):
        return "\n".join(f"{k}: {v}" for k, v in feelings.items())
    if isinstance(feelings, list):
        return "\n".join(str(item) for item in feelings)
    return str(feelings)


def save_emotional_arc(
    vignette: str, feelings: str, cohesion: str | None = None
) -> None:
    """Save the emotional arc information to the gdsf file."""
    parsed_cohesion = None
    if cohesion not in (None, ""):
        try:
            parsed_cohesion = json.loads(cohesion)
        except Exception:
            parsed_cohesion = cohesion

    parsed_feelings = _parse_feelings(feelings)

    data = _load_data()
    payload = {"vignette": vignette, "feelings": parsed_feelings}
    if parsed_cohesion is not None:
        payload["cohesion"] = parsed_cohesion
    data["emotional_arc"] = {"value": json.dumps(payload)}
    _save_data(data)


def load_emotional_arc():
    data = _load_data()
    raw = data.get("emotional_arc", {}).get("value", "")
    try:
        return json.loads(raw)
    except Exception:
        return {}


# ---------------------------------------------------------------------------
# Step 5: Layer Feelings helpers

def _parse_layered_feelings(text: str) -> dict:
    """Parse dash-prefixed text into a nested dictionary."""
    # attempt JSON first for backwards compatibility
    try:
        loaded = json.loads(text)
        if isinstance(loaded, dict):
            return loaded
    except Exception:
        pass

    lines = [l.rstrip() for l in text.splitlines() if l.strip()]
    root: dict[str, dict] = {}
    stack: list[tuple[int, dict]] = [(0, root)]

    for line in lines:
        stripped = line.lstrip()
        m = re.match(r"^(?P<dashes>-+)", stripped)
        if m:
            level = len(m.group("dashes"))
            label = stripped[m.end():].strip()
        else:
            # allow space-indented bullets
            m2 = re.match(r"^( *)-+\s*(.+)$", line)
            if m2:
                level = int(len(m2.group(1)) / 2) + 1
                label = m2.group(2).strip()
            else:
                level = 1
                label = stripped

        while stack and stack[-1][0] >= level:
            stack.pop()
        parent = stack[-1][1]
        parent[label] = {}
        stack.append((level, parent[label]))

    return root


def layered_feelings_to_text(data: dict, level: int = 1) -> str:
    """Convert nested feelings structure back into dash-prefixed lines."""
    lines: list[str] = []
    for key, value in data.items():
        lines.append(f"{'-' * level} {key}")
        if isinstance(value, dict) and value:
            lines.append(layered_feelings_to_text(value, level + 1))
    return "\n".join(lines)


def save_layered_feelings(structure: str) -> None:
    """Save the optional Layer Feelings structure."""
    parsed = _parse_layered_feelings(structure)

    data = _load_data()
    data["layered_feelings"] = {"value": json.dumps(parsed)}
    _save_data(data)


def load_layered_feelings():
    data = _load_data()
    raw = data.get("layered_feelings", {}).get("value", "")
    try:
        return json.loads(raw)
    except Exception:
        return raw


# ---------------------------------------------------------------------------
# Step 6: Base Mechanics Tree helpers

def save_base_mechanics_tree(structure: str) -> None:
    """Save the Base Mechanics Tree structure."""
    parsed = _parse_layered_feelings(structure)

    data = _load_data()
    data["base_mechanics_tree"] = {"value": json.dumps(parsed)}
    _save_data(data)


def load_base_mechanics_tree():
    data = _load_data()
    raw = data.get("base_mechanics_tree", {}).get("value", "")
    try:
        return json.loads(raw)
    except Exception:
        return raw


def flatten_mechanics(tree: dict) -> list:
    """Return a flat list of unique mechanics in a BMT."""
    result: list[str] = []
    seen: set[str] = set()

    def recurse(node: dict) -> None:
        for k, v in node.items():
            if k not in seen:
                seen.add(k)
                result.append(k)
            if isinstance(v, dict):
                recurse(v)

    recurse(tree)
    return result


# ---------------------------------------------------------------------------
# Step 6A helpers - mechanic mappings and BMT construction

def _parse_mechanic_mappings(text: str) -> dict:
    """Convert user text into a mapping of feeling -> [mechanics]."""
    try:
        loaded = json.loads(text)
        if isinstance(loaded, dict):
            parsed = {}
            for k, v in loaded.items():
                if isinstance(v, list):
                    parsed[k] = [str(i).strip() for i in v]
                else:
                    parsed[k] = [str(v).strip()]
            return parsed
    except Exception:
        pass

    result: dict[str, list[str]] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        for sep in ("->", ":", "="):
            if sep in line:
                feeling, mechs = line.split(sep, 1)
                break
        else:
            continue
        result[feeling.strip()] = [m.strip() for m in re.split(r"[;,]", mechs) if m.strip()]
    return result


def mechanic_mappings_to_text(mapping: dict) -> str:
    return "\n".join(f"{k}: {', '.join(v)}" for k, v in mapping.items())


def save_mechanic_mappings(mappings: str) -> None:
    parsed = _parse_mechanic_mappings(mappings)
    data = _load_data()
    data["mechanic_mappings"] = {"value": json.dumps(parsed)}
    _save_data(data)


def load_mechanic_mappings():
    data = _load_data()
    raw = data.get("mechanic_mappings", {}).get("value", "")
    try:
        return json.loads(raw)
    except Exception:
        return raw


def build_base_mechanics_tree(layered_feelings: dict, mapping: dict) -> dict:
    """Create a Base Mechanics Tree by replacing feelings with mechanics."""

    def merge(dst: dict, src: dict) -> None:
        for k, v in src.items():
            if k in dst:
                merge(dst[k], v)
            else:
                dst[k] = v

    def recurse(node: dict) -> dict:
        result: dict[str, dict] = {}
        for feeling, sub in node.items():
            mechs = mapping.get(feeling, [feeling])
            child = recurse(sub)
            for mech in mechs:
                if mech not in result:
                    result[mech] = {}
                merge(result[mech], child)
        return result

    return recurse(layered_feelings)


# ---------------------------------------------------------------------------
# Step 7: List of Schemas helpers

def _parse_schemas(text: str) -> list:
    """Convert user text into a list of schema dictionaries."""
    try:
        data = json.loads(text)
        if isinstance(data, list):
            return data
    except Exception:
        pass

    schemas = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if ":" in line:
            name, prop = line.split(":", 1)
            schemas.append({"name": name.strip(), "property": prop.strip()})
        else:
            schemas.append({"name": line})
    return schemas


def schemas_to_text(schemas: list) -> str:
    """Serialize a schema list back into readable text."""
    lines = []
    for item in schemas:
        name = item.get("name", "")
        prop = item.get("property")
        if prop:
            lines.append(f"{name}: {prop}")
        else:
            lines.append(name)
    return "\n".join(lines)


def save_list_of_schemas(schemas: str) -> None:
    parsed = _parse_schemas(schemas)
    data = _load_data()
    data["list_of_schemas"] = {"value": json.dumps(parsed)}
    _save_data(data)


def load_list_of_schemas():
    data = _load_data()
    raw = data.get("list_of_schemas", {}).get("value", "")
    try:
        return json.loads(raw)
    except Exception:
        return raw


# ---------------------------------------------------------------------------
# Step 7 queue persistence helpers

def save_step7_queue(queue: list) -> None:
    """Persist the remaining Step 7 queue to the gdsf file."""
    data = _load_data()
    data["step7_queue"] = {"value": json.dumps(queue)}
    _save_data(data)


def load_step7_queue() -> list:
    """Load the saved Step 7 queue if present."""
    data = _load_data()
    raw = data.get("step7_queue", {}).get("value", "")
    try:
        return json.loads(raw)
    except Exception:
        return []

# ---------------------------------------------------------------------------
# Step 8: Scaling Influence Table helpers

def _parse_sit(text: str) -> dict:
    """Parse SIT text into a dict mapping ``skill -> {emotion: '+'|'-'}``.

    Accepts either JSON or a simple ``skill: emotion +/-`` line format.
    Lines may contain multiple comma/semicolon separated pairs, e.g.::

        Planning: Progress +, Constant Pressure -
    """

    try:
        loaded = json.loads(text)
        if isinstance(loaded, dict):
            parsed: dict[str, dict[str, str]] = {}
            for k, v in loaded.items():
                if isinstance(v, dict):
                    parsed[str(k)] = {str(ek): str(ev) for ek, ev in v.items()}
                elif isinstance(v, list):
                    # Backwards compatibility for old list-only format
                    parsed[str(k)] = {str(ek): "+" for ek in v}
            return parsed
    except Exception:
        pass

    result: dict[str, dict[str, str]] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        for sep in ("->", ":", "="):
            if sep in line:
                skill, emos = line.split(sep, 1)
                break
        else:
            continue
        emo_map: dict[str, str] = {}
        for part in re.split(r"[;,]", emos):
            part = part.strip()
            if not part:
                continue
            tokens = part.split()
            if len(tokens) == 2:
                emo, mark = tokens
            else:
                emo, mark = tokens[0], "+"
            emo_map[emo.strip()] = mark.strip()
        result[skill.strip()] = emo_map
    return result


def sit_to_text(table: dict) -> str:
    """Convert a SIT mapping to a human-readable string."""
    lines: list[str] = []
    for skill, emos in table.items():
        if isinstance(emos, dict):
            entries = [f"{e} {v}" for e, v in emos.items()]
            lines.append(f"{skill}: {', '.join(entries)}")
        elif isinstance(emos, list):
            # Backwards compatibility for old list-only format
            lines.append(f"{skill}: {', '.join(emos)}")
        else:
            lines.append(f"{skill}: {emos}")
    return "\n".join(lines)


def save_sit(table: str | dict) -> None:
    if isinstance(table, dict):
        parsed = table
    else:
        parsed = _parse_sit(table)
    data = _load_data()
    data["sit_table"] = {"value": json.dumps(parsed)}
    _save_data(data)


def load_sit():
    data = _load_data()
    raw = data.get("sit_table", {}).get("value", "")
    try:
        return json.loads(raw)
    except Exception:
        return raw


# ---------------------------------------------------------------------------
# Step 8B: Triadic Integration Table helpers


def save_tit(table: str | dict) -> None:
    """Persist the Triadic Integration Table."""

    if isinstance(table, dict):
        parsed = table
    else:
        try:
            parsed = json.loads(table)
        except Exception:
            parsed = {}

    data = _load_data()
    data["tit_table"] = {"value": json.dumps(parsed)}
    _save_data(data)


def load_tit():
    """Load the stored Triadic Integration Table."""

    data = _load_data()
    raw = data.get("tit_table", {}).get("value", "")
    try:
        return json.loads(raw)
    except Exception:
        return raw


def _find_subtree(tree: dict, target: str):
    """Return the subtree rooted at ``target`` if present."""

    if not isinstance(tree, dict):
        return None
    if target in tree:
        return tree[target]
    for _, val in tree.items():
        if isinstance(val, dict):
            found = _find_subtree(val, target)
            if found is not None:
                return found
    return None


def _collect_nodes(node: dict) -> list[str]:
    """Collect all node names from a nested mapping."""

    result: list[str] = []
    if not isinstance(node, dict):
        return result
    for key, val in node.items():
        result.append(key)
        if isinstance(val, dict):
            result.extend(_collect_nodes(val))
    return result


def get_schemas_for_emotion(emotion: str) -> list[str]:
    """Return all mechanics and schemas linked to an emotion."""

    mappings = load_mechanic_mappings()
    if isinstance(mappings, dict):
        mechanics = mappings.get(emotion, [])
    else:
        mechanics = []

    bmt = load_base_mechanics_tree()
    schemas: list[str] = []

    for mech in mechanics:
        schemas.append(mech)
        subtree = _find_subtree(bmt, mech) if isinstance(bmt, dict) else None
        if isinstance(subtree, dict):
            schemas.extend(_collect_nodes(subtree))

    # remove duplicates while preserving order
    seen: set[str] = set()
    ordered: list[str] = []
    for item in schemas:
        if item not in seen:
            seen.add(item)
            ordered.append(item)
    return ordered
