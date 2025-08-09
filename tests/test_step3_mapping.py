import json
from pathlib import Path
import sys
import types

# Provide dummy modules for optional dependencies
sys.modules.setdefault("dotenv", types.SimpleNamespace(load_dotenv=lambda **kwargs: None))

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))
import ui.ai as ai  # noqa: E402


def test_step3_mapping_runs_per_kernel(monkeypatch):
    calls = []

    def fake_step3b(theme, kernels):
        calls.append(kernels[0]["id"])
        return json.dumps({"kernels": [{"kernel": kernels[0]["kernel"]}]})

    monkeypatch.setattr(ai, "step3b", fake_step3b)

    skill_kernels = {
        "Declarative": [{"id": "k1", "kernel": "A"}],
        "Procedural": [{"id": "k2", "kernel": "B"}],
    }

    result = ai.step3_mapping("Theme", skill_kernels)
    data = json.loads(result)

    assert calls == ["k1", "k2"]
    assert data["kernels"] == [{"kernel": "A"}, {"kernel": "B"}]

