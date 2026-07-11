"""Unit tests for psse_utils.filter_taralog_notcnv._parse_args (the CLI contract).

Fast and fixture-free: assert which arguments are required, defaults, and
that --con accepts one or more values (globs are expanded later, not here).
"""
from __future__ import annotations

from pathlib import Path

import pytest

from psse_utils.filter_taralog_notcnv import _parse_args

REQUIRED = ["--taralog", "taralog.txt", "--con", "a.con"]


def test_required_args_parse_into_expected_types():
    ns = _parse_args(REQUIRED)
    assert ns.taralog == Path("taralog.txt")
    assert ns.con_patterns == ["a.con"]
    assert ns.out_dir is None


def test_con_accepts_multiple_values():
    ns = _parse_args(["--taralog", "t.txt", "--con", "a.con", "b.con", "*.con"])
    assert ns.con_patterns == ["a.con", "b.con", "*.con"]


def test_out_dir_optional_override():
    ns = _parse_args(REQUIRED + ["--out-dir", "out"])
    assert ns.out_dir == Path("out")


@pytest.mark.parametrize("drop", ["--taralog", "--con"])
def test_each_required_arg_is_enforced(drop):
    """Removing any one required flag (and its value) must abort with
    SystemExit from argparse."""
    argv = []
    skip = False
    for tok in REQUIRED:
        if tok == drop:
            skip = True
            continue
        if skip:
            skip = False
            continue
        argv.append(tok)
    with pytest.raises(SystemExit):
        _parse_args(argv)
