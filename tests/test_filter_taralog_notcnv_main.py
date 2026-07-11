"""End-to-end tests for psse_utils.filter_taralog_notcnv.main().

main() runs the full pipeline in-process (find NotCnv names in taralog.txt
-> expand --con glob patterns -> filter each .con file -> write
<stem>-NotCnv.con) and returns an exit code.
"""
from __future__ import annotations

from psse_utils.filter_taralog_notcnv import main


def _run(taralog_file, con_args, out_dir=None):
    argv = ["--taralog", str(taralog_file), "--con", *con_args]
    if out_dir is not None:
        argv += ["--out-dir", str(out_dir)]
    return main(argv)


def test_main_happy_path_writes_filtered_con_files(taralog_file, con_file_a, con_file_b, tmp_path):
    rc = _run(taralog_file, [str(con_file_a), str(con_file_b)], tmp_path)
    assert rc == 0
    out_a = tmp_path / "sample_a-NotCnv.con"
    out_b = tmp_path / "sample_b-NotCnv.con"
    assert out_a.exists()
    assert out_b.exists()
    assert "FAKE LINE ALPHA 138_SRT-A" in out_a.read_text(encoding="utf-8")
    assert "FAKE UNIT ECHO 2_SRT-A" in out_b.read_text(encoding="utf-8")


def test_main_expands_glob_pattern(taralog_file, con_file_a, con_file_b, tmp_path):
    pattern = str(con_file_a.parent / "sample_*.con")
    rc = _run(taralog_file, [pattern], tmp_path)
    assert rc == 0
    assert (tmp_path / "sample_a-NotCnv.con").exists()
    assert (tmp_path / "sample_b-NotCnv.con").exists()


def test_main_default_out_dir_is_alongside_input(taralog_file, con_file_a, tmp_path):
    """Without --out-dir, the filtered copy lands next to the input file."""
    copy = tmp_path / "sample_a.con"
    copy.write_text(con_file_a.read_text(encoding="utf-8"), encoding="utf-8")
    rc = _run(taralog_file, [str(copy)])
    assert rc == 0
    assert (tmp_path / "sample_a-NotCnv.con").exists()


def test_main_missing_taralog_returns_nonzero(tmp_path, con_file_a, capsys):
    rc = _run(tmp_path / "does_not_exist.txt", [str(con_file_a)])
    assert rc != 0
    assert "not found" in capsys.readouterr().err


def test_main_reports_missing_con_file_without_crashing(taralog_file, tmp_path, capsys):
    missing = tmp_path / "ghost.con"
    rc = _run(taralog_file, [str(missing)], tmp_path)
    assert rc == 0
    assert "SKIP" in capsys.readouterr().out


def test_main_prints_summary_counts(taralog_file, con_file_a, tmp_path, capsys):
    _run(taralog_file, [str(con_file_a)], tmp_path)
    out = capsys.readouterr().out
    assert "Non-convergent (NotCnv) contingency names found" in out
    assert "kept=3, skipped=1" in out
