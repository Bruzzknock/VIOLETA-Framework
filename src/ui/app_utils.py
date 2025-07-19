import json
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
                f.write(f"{k} = \"{v}\"\n")
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


def _split_theme(theme: str):
    """Split a theme string into name and description."""
    lines = [l.strip() for l in theme.splitlines() if l.strip()]
    if not lines:
        return "", ""
    name = lines[0]
    desc = "\n".join(lines[1:]).strip()
    return name, desc


def save_theme(theme: str) -> None:
    """Save theme text as separate name and description fields."""
    name, desc = _split_theme(theme)
    data = _load_data()
    data["theme"] = {"name": name, "description": desc}
    _save_data(data)


def load_theme() -> str:
    """Load theme as a single text blob for display."""
    data = _load_data()
    theme = data.get("theme", {})
    if "name" in theme:
        text = theme.get("name", "")
        if theme.get("description"):
            text += "\n" + theme["description"]
        return text
    return theme.get("value", "")


def load_theme_dict() -> dict:
    """Return theme as a dictionary with name and description."""
    data = _load_data()
    theme = data.get("theme", {})
    if "name" in theme:
        return theme
    name, desc = _split_theme(theme.get("value", ""))
    return {"name": name, "description": desc}


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
        try:
            return json.loads(raw[1:-1])
        except Exception:
            return raw


# Adding new kernel mapping functions

def save_kernel_mappings(mappings) -> None:
    """Save kernel mapping table to the gdsf file."""
    if isinstance(mappings, str):
        try:
            parsed = json.loads(mappings)
        except Exception:
            parsed = mappings
    else:
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
def save_kernel_theme_mapping(info) -> None:
    """Save Step 3B table to the gdsf file."""
    if isinstance(info, str):
        try:
            parsed = json.loads(info)
        except Exception:
            parsed = info
    else:
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
