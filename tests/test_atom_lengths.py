"""Unit tests for codegraphcl.atom_lengths (Phase 3.1 length-control checker)."""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from codegraphcl.atom_lengths import main, _tokens

def _tmp_task(tmp_path, body):
    td = tmp_path / "tasks" / "x"
    (td).mkdir(parents=True)
    (td / "atoms_ablation.md").write_text(body)
    return td

ATOMS = """\
# ablation
<!-- ATOM:correct_short -->
short correct one two three four
<!-- /ATOM:correct_short -->
<!-- ATOM:irrelevant_short -->
short irrelevant one two three four
<!-- /ATOM:irrelevant_short -->
<!-- ATOM:correct_long -->
long correct one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen
<!-- /ATOM:correct_long -->
<!-- ATOM:irrelevant_long -->
long irrelevant one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen
<!-- /ATOM:irrelevant_long -->
"""

def test_passes_when_matched(tmp_path):
    td = _tmp_task(tmp_path, ATOMS)
    assert main(str(td), "atoms_ablation.md") == 0  # both pairs <= 5%

def test_fails_when_unmatched(tmp_path):
    body = ATOMS.replace("short correct one two three four",
                         "short correct one two three four five six seven eight nine ten eleven")
    td = _tmp_task(tmp_path, body)
    assert main(str(td), "atoms_ablation.md") == 1  # short pair now > 5%

def test_tokens():
    assert _tokens("hello world") > 0
    assert _tokens("") == 0

def test_missing_file(tmp_path, capsys):
    td = _tmp_task(tmp_path, ATOMS)
    assert main(str(td), "nope.md") == 1
