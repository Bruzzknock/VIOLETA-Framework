import json
import sys
import types
from pathlib import Path

# Ensure src directory is available for imports
sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

# Provide a minimal stub for the optional 'dotenv' dependency required by ui.ai
dotenv_stub = types.ModuleType("dotenv")
dotenv_stub.load_dotenv = lambda *args, **kwargs: None
sys.modules.setdefault("dotenv", dotenv_stub)

from ui.ai import step3b

def test_step3b_preserves_declarative_kernel():
    skill_kernels = {
        "Skill": [
            {
                "kernel": "Original kernel",
                "input": "input",
                "verb": "do",
                "output": "output",
                "type": "declarative",
            }
        ]
    }
    theme = "Test Theme"
    result = step3b(theme, skill_kernels)
    data = json.loads(result)
    assert data["theme"] == theme
    assert data["kernels"] == [
        {
            "kernel": "Original kernel",
            "input": "input",
            "verb": "do",
            "output": "output",
            "type": "declarative",
            "preserved": "Y",
        }
    ]

