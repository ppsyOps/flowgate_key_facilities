"""Filter PSS/E .con contingency files down to only the non-convergent
(NotCnv) contingencies reported in a TARA/PowerGEM taralog.txt.

Usage:
    filter-taralog-notcnv --taralog taralog.txt --con file1.con [file2.con ...]
    filter-taralog-notcnv --taralog taralog.txt --con "*.con" --out-dir out/

--con accepts glob patterns (e.g. "*.con"). They are expanded by this script
so wildcards work the same on Windows (cmd/PowerShell do not expand them for
external programs) and on Linux/macOS.

Each matched .con file is copied to <out-dir or alongside the input>/<stem>-NotCnv<suffix>,
containing only the contingency blocks whose name matches a NotCnv contingency
found anywhere in taralog.txt (pooled across all repeated report sections).
"""
from __future__ import annotations

import argparse
import glob
import re
import sys
from pathlib import Path

# 0-based column where the "NotCnv " status token starts in taralog.txt.
# Confirmed against real PowerGEM/TARA output: constant regardless of Cont
# ID / Cont Name width.
NOTCNV_COL = 139

# Everything up to NOTCNV_COL is "<Cont ID><whitespace><Cont Name padding>".
CONT_ROW_RE = re.compile(r"\s*\d+\s+(.+)")

# A contingency block starts with "contingency <name>" (case-insensitive,
# any leading whitespace). Names are normally quoted ('...' or "..."), but
# real-world data sometimes has unmatched/missing quotes, so quotes are
# stripped rather than required to match. Lines commented out with a
# leading "/" (or "//") are not matched, since "/" is not whitespace.
CON_START_RE = re.compile(r"^\s*contingency\s+(\S.*)$", re.IGNORECASE)
CON_END_RE = re.compile(r"^\s*end\s*$", re.IGNORECASE)


def normalize(name: str) -> str:
    """Strip whitespace and one layer of surrounding quotes, casefold."""
    name = name.strip()
    if len(name) >= 2 and name[0] in "'\"" and name[-1] == name[0]:
        name = name[1:-1]
    elif name[:1] in "'\"":
        name = name[1:]
    return name.strip().casefold()


def expand_con_patterns(patterns: list[str]) -> list[Path]:
    """Expand glob patterns (e.g. "*.con") into matching paths. A pattern
    with no matches is kept as-is so the caller can report it as not found."""
    paths: list[Path] = []
    for pattern in patterns:
        matches = sorted(glob.glob(pattern))
        if matches:
            paths.extend(Path(m) for m in matches)
        else:
            paths.append(Path(pattern))
    return paths


def find_notcnv_names(taralog_path: Path) -> set[str]:
    """Return the normalized set of contingency names marked NotCnv anywhere
    in taralog.txt (pooled across all repeated report sections)."""
    names = set()
    text = taralog_path.read_text(encoding="utf-8-sig", errors="replace")
    for line in text.splitlines():
        if line[NOTCNV_COL : NOTCNV_COL + 7].casefold() != "notcnv ":
            continue
        m = CONT_ROW_RE.match(line[:NOTCNV_COL])
        if m:
            names.add(normalize(m.group(1)))
    return names


def filter_con_file(con_path: Path, keep_names: set[str], out_dir: Path | None) -> tuple[Path, int, int]:
    """Write a copy of con_path containing only contingency blocks whose
    name is in keep_names. Returns (output_path, kept_count, skipped_count)."""
    lines = con_path.read_text(encoding="utf-8-sig", errors="replace").splitlines(keepends=True)
    out_lines: list[str] = []
    block: list[str] = []
    in_block = False
    keep_block = False
    kept = skipped = 0

    for line in lines:
        stripped = line.rstrip("\r\n")
        start = CON_START_RE.match(stripped)
        if start:
            in_block = True
            keep_block = normalize(start.group(1)) in keep_names
            block = [line]
            continue
        if in_block:
            block.append(line)
            if CON_END_RE.match(stripped):
                if keep_block:
                    out_lines.extend(block)
                    kept += 1
                else:
                    skipped += 1
                in_block = False
                block = []
            continue
        out_lines.append(line)

    out_path = (out_dir or con_path.parent) / f"{con_path.stem}-NotCnv{con_path.suffix}"
    out_path.write_text("".join(out_lines), encoding="utf-8")
    return out_path, kept, skipped


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--taralog", required=True, type=Path, help="Path to taralog.txt")
    p.add_argument(
        "--con", required=True, nargs="+", dest="con_patterns",
        help="One or more .con files or glob patterns (e.g. *.con) to filter",
    )
    p.add_argument(
        "--out-dir", type=Path, default=None,
        help="Output directory (default: alongside each input .con file)",
    )
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)

    if not args.taralog.is_file():
        print(f"taralog file not found: {args.taralog}", file=sys.stderr)
        return 1

    keep_names = find_notcnv_names(args.taralog)
    print(f"Non-convergent (NotCnv) contingency names found in {args.taralog.name}: {len(keep_names)}")

    if args.out_dir:
        args.out_dir.mkdir(parents=True, exist_ok=True)

    for con_path in expand_con_patterns(args.con_patterns):
        if not con_path.is_file():
            print(f"  SKIP (not found): {con_path}")
            continue
        out_path, kept, skipped = filter_con_file(con_path, keep_names, args.out_dir)
        print(f"  {con_path.name}: kept={kept}, skipped={skipped} -> {out_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
