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


def save_atomic_unit(value: str) -> None:
    data = _load_data()
    data["atomic_unit"] = {"value": value}
    _save_data(data)


def load_atomic_unit() -> str:
    data = _load_data()
    return data.get("atomic_unit", {}).get("value", "")


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
