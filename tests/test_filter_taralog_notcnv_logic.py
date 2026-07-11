"""Unit tests for the importable logic functions in
psse_utils.filter_taralog_notcnv (normalize, expand_con_patterns,
find_notcnv_names, filter_con_file), independent of the CLI.
"""
from __future__ import annotations

from psse_utils.filter_taralog_notcnv import (
    expand_con_patterns,
    filter_con_file,
    find_notcnv_names,
    normalize,
)

# Expected NotCnv names in tests/data/taralog_sample.txt, pooled across its
# two synthetic report sections (see the fixture for the raw rows):
#   FAKE LINE ALPHA 138_SRT-A   -- NotCnv in both sections (duplicate -> dedup)
#   FAKE LINE GAMMA 500_SRT-A   -- NotCnv in section 1 only
#   FAKE UNIT ECHO 2_SRT-A      -- NotCnv in section 1 only
#   FAKE UNIT DELTA 1_SRT-A     -- NotCnv in section 2 only
# FAKE LINE BETA 138_SRT-A / FAKE LINE FOXTROT 230_SRT-A are "Vlt" (not NotCnv).
EXPECTED_NOTCNV_NAMES = {
    "fake line alpha 138_srt-a",
    "fake line gamma 500_srt-a",
    "fake unit echo 2_srt-a",
    "fake unit delta 1_srt-a",
}


def test_normalize_strips_matched_quotes_and_whitespace():
    assert normalize("  'FOO BAR'  ") == "foo bar"
    assert normalize('"FOO BAR"') == "foo bar"
    assert normalize("FOO BAR") == "foo bar"


def test_normalize_strips_unmatched_leading_quote():
    """Real .con data sometimes has a missing closing quote."""
    assert normalize('"FOO BAR') == "foo bar"


def test_find_notcnv_names_pools_and_dedupes_across_sections(taralog_file):
    names = find_notcnv_names(taralog_file)
    assert names == EXPECTED_NOTCNV_NAMES


def test_expand_con_patterns_expands_glob(con_file_a, con_file_b):
    pattern = str(con_file_a.parent / "sample_*.con")
    paths = expand_con_patterns([pattern])
    assert set(paths) == {con_file_a, con_file_b}


def test_expand_con_patterns_keeps_unmatched_pattern_literal(tmp_path):
    missing = tmp_path / "nomatch*.con"
    paths = expand_con_patterns([str(missing)])
    assert paths == [missing]


def test_filter_con_file_keeps_only_matching_blocks(con_file_a, tmp_path):
    out_path, kept, skipped = filter_con_file(con_file_a, EXPECTED_NOTCNV_NAMES, tmp_path)
    assert out_path == tmp_path / "sample_a-NotCnv.con"
    # sample_a.con: ALPHA (match), BETA (no match), GAMMA (match), DELTA (match)
    assert kept == 3
    assert skipped == 1
    text = out_path.read_text(encoding="utf-8")
    assert "FAKE LINE ALPHA 138_SRT-A" in text
    assert "FAKE LINE GAMMA 500_SRT-A" in text
    assert "FAKE UNIT DELTA 1_SRT-A" in text
    assert "FAKE LINE BETA 138_SRT-A" not in text


def test_filter_con_file_handles_malformed_quote_and_comment(con_file_b, tmp_path):
    out_path, kept, skipped = filter_con_file(con_file_b, EXPECTED_NOTCNV_NAMES, tmp_path)
    # sample_b.con: ECHO (double-quote, match), DELTA (malformed quote, match),
    # a "/"-commented ALPHA block (not a real block, doesn't count), UNMATCHED (no match)
    assert kept == 2
    assert skipped == 1
    text = out_path.read_text(encoding="utf-8")
    assert "FAKE UNIT ECHO 2_SRT-A" in text
    assert "FAKE UNIT DELTA 1_SRT-A" in text
    assert "FAKE LINE UNMATCHED_SRT-A" not in text
    # The "/"-commented block is not recognized as a contingency block (kept
    # == 2 above proves it wasn't counted), but the comment text itself is
    # preserved verbatim as passthrough, same as any other non-block content.
    assert '/contingency "FAKE LINE ALPHA 138_SRT-A"' in text
