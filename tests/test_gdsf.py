import tempfile
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))
from gdsf import GDSFParser

def test_schema_without_property():
    content = """[schema]
id = T1
name = \"Foo\"
"""  # no property field
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "test.gdsf"
        path.write_text(content)
        parser = GDSFParser(path)
        assert any(s.get("id") == "T1" for s in parser.schemas)


def test_multiline_values_with_blank_lines():
    content = (
        "[theme]\n"
        "value = \"Line1\n\nLine3\"\n"
    )
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "test.gdsf"
        path.write_text(content)
        parser = GDSFParser(path)
        assert parser.get_section("theme") == {"value": "Line1\n\nLine3"}

