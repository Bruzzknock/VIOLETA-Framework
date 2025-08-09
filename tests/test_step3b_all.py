import json
from pathlib import Path
import sys
import types

# Provide dummy modules for optional dependencies
sys.modules.setdefault("dotenv", types.SimpleNamespace(load_dotenv=lambda **kwargs: None))

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))
import ui.ai as ai  # noqa: E402


def test_step3b_all(monkeypatch):
    calls = []

    def fake_step3b(theme, kernels):
        calls.append(kernels)
        return json.dumps({"kernels": [{"kernel": kernels[0]["k"]}]})

    monkeypatch.setattr(ai, "step3b", fake_step3b)

    kernels = [{"k": "one"}, {"k": "two"}]
    result = ai.step3b_all("T", kernels)

    assert calls == [[{"k": "one"}], [{"k": "two"}]]
    assert result == {"kernels": [{"kernel": "one"}, {"kernel": "two"}]}
