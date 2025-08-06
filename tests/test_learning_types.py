import tempfile
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))
import ui.app_utils as app_utils  # noqa: E402


def test_save_load_learning_types(tmp_path, monkeypatch):
    # Redirect data path to temporary directory
    data_dir = tmp_path
    gdsf_file = data_dir / "info.gdsf"
    monkeypatch.setattr(app_utils, "DATA_PATH", data_dir)
    monkeypatch.setattr(app_utils, "GDSF_FILE", gdsf_file)
    types = ["Declarative", "Procedural"]
    app_utils.save_learning_types(types)
    assert app_utils.load_learning_types() == types
