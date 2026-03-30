#!/usr/bin/env python3
"""
Tests ALL examples from every T*.md grammar file.
Prints ✅ / ❌ for each clue, grouped by file.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src" / "python"))
from grammar_loader import GRAMMAR_DIR, load_parser, preprocess_clue

from lark import UnexpectedInput


# ---------------------------------------------------------------------------
# Collect names and jobs from example rows in T*.md files
# ---------------------------------------------------------------------------

def _extract_names_from_pos(text: str, names: set[str]) -> None:
    """Pull person names out of composite pos/parity_count cell values."""
    for pat in (
        r"\bneighboring\s+(\w+)",
        r"\b(?:below|above)\s+(\w+)",
        r"\bto the (?:left|right) of\s+(\w+)",
        r"\bin between\s+(\w+)(?:\s+and\s+(\w+))?",
    ):
        for m in re.finditer(pat, text):
            names.update(w for w in m.groups() if w)
    for m in re.finditer(r"(\w+)'s", text):
        names.add(m.group(1))


def collect_names_and_jobs() -> tuple[list[str], list[str]]:
    names: set[str] = set()
    jobs: set[str] = set()

    COMPOSITE_COLS = {"pos", "parity_count", "super_pos", "nb_with_opt_filter"}

    for md_file in sorted(GRAMMAR_DIR.glob("T*.md")):
        content = md_file.read_text()
        lines = content.splitlines()

        header_line = next(
            (l for l in lines if l.strip().startswith("|") and "---" not in l), None
        )
        if not header_line:
            continue
        col_headers = [c.strip() for c in header_line.split("|") if c.strip()]

        sep_found = False
        for line in lines:
            if "---" in line:
                sep_found = True
                continue
            if not sep_found or not line.strip().startswith("|"):
                continue
            cells = [c.strip() for c in line.split("|") if c.strip()]
            if not cells:
                continue

            for header, cell in zip(col_headers, cells):
                val = cell.strip().replace("\u00a0", " ").lower()
                if not val:
                    continue
                if header == "NAME":
                    names.add(val)
                elif header == "NAME_S":
                    if val.endswith("'s"):
                        names.add(val[:-2])
                elif header == "job":
                    # store both singular and plural
                    jobs.add(val)
                    if val.endswith("s") and len(val) > 2:
                        jobs.add(val[:-1])
                elif header in COMPOSITE_COLS or "pos" in header:
                    _extract_names_from_pos(val, names)

    return sorted(names), sorted(jobs)


# ---------------------------------------------------------------------------
# Load all examples from T*.md files
# ---------------------------------------------------------------------------

def load_all_examples() -> list[tuple[str, str, str]]:
    """Return list of (expected_alias, clue_text, filename)."""
    examples = []
    for md_file in sorted(GRAMMAR_DIR.glob("T*.md")):
        expected_alias = md_file.stem.lower()
        content = md_file.read_text()
        lines = content.splitlines()

        sep_found = False
        for line in lines:
            if "---" in line:
                sep_found = True
                continue
            if not sep_found or not line.strip().startswith("|"):
                continue
            cells = [c.strip() for c in line.split("|") if c.strip()]
            if not cells:
                continue
            # Reconstruct the clue by joining all cell values
            clue_text = " ".join(c.replace("\u00a0", " ") for c in cells)
            examples.append((expected_alias, clue_text, md_file.name))

    return examples


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    names, jobs = collect_names_and_jobs()
    parser = load_parser(names, jobs)
    examples = load_all_examples()

    ok = fail = 0
    current_file = None

    for expected, clue, filename in examples:
        if filename != current_file:
            if current_file is not None:
                print()
            current_file = filename
            print(f"  {filename}")

        preprocessed = preprocess_clue(clue)
        try:
            tree = parser.parse(preprocessed)
            matched = tree.children[0].data
            if matched == expected:
                print(f"    ✅  {clue}")
                ok += 1
            else:
                print(f"    ❌  {clue}")
                print(f"         attendu {expected!r}, obtenu {matched!r}")
                fail += 1
        except UnexpectedInput as e:
            print(f"    ❌  {clue}")
            print(f"         {str(e).splitlines()[0]}")
            fail += 1

    total = ok + fail
    print()
    print("─" * 64)
    icon = "✅" if fail == 0 else "❌"
    print(f"  {icon}  {ok}/{total} passed", end="")
    if fail:
        print(f"  ({fail} failed)")
    else:
        print()


if __name__ == "__main__":
    main()
