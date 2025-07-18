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
