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


def save_atomic_skills(skills) -> None:
    if not isinstance(skills, str):
        skills = json.dumps(skills)
    data = _load_data()
    data["atomic_skills"] = {"value": skills}
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
