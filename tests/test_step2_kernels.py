import json
from types import SimpleNamespace
from pathlib import Path
import sys
import types

# Provide dummy modules for optional dependencies
sys.modules.setdefault("dotenv", types.SimpleNamespace(load_dotenv=lambda **kwargs: None))

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))
import ui.ai as ai  # noqa: E402


def test_step2_kernels_prompts(monkeypatch):
    recorded = {}

    class FakeModel:
        def invoke(self, messages):
            skill_line = next(m.content for m in messages if m.content.startswith("Atomic skill"))
            skill = skill_line.split(": ", 1)[1]
            recorded[skill] = messages[0].content
            fake = {skill: [{"kernel": "k", "input": "i", "verb": "v", "output": "o"}]}
            return SimpleNamespace(content=json.dumps(fake))

    monkeypatch.setattr(ai, "get_llm", lambda: FakeModel())

    atomic_skills = {
        "Declarative": ["Fact"],
        "Procedural": ["Action"],
        "Metacognitive": ["Reflection"],
    }

    result = ai.step2_kernels("Unit", atomic_skills)
    data = json.loads(result)
    assert set(data.keys()) == {"Fact", "Action", "Reflection"}
    assert "passive" in recorded["Fact"].lower()
    assert "imperative" in recorded["Action"].lower()
    assert "cognitive" in recorded["Reflection"].lower()
