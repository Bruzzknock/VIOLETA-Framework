import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))
import ui.app_utils as app_utils  # noqa: E402


def test_save_load_atomic_skills_per_type(tmp_path, monkeypatch):
    data_dir = tmp_path
    gdsf_file = data_dir / "info.gdsf"
    monkeypatch.setattr(app_utils, "DATA_PATH", data_dir)
    monkeypatch.setattr(app_utils, "GDSF_FILE", gdsf_file)

    skills = {"Declarative": ["fact1", "fact2"], "Procedural": ["step1"]}
    app_utils.save_atomic_skills(skills)
    assert app_utils.load_atomic_skills() == skills
