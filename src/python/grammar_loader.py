"""Shared grammar utilities used by main.py and test_grammar.py."""
from pathlib import Path

from lark import Lark

GRAMMAR_DIR = Path(__file__).parent.parent.parent / "grammar"


def cell_to_lark(cell: str) -> str:
    if cell.startswith('"') and cell.endswith('"'):
        return '"' + cell[1:-1].lower() + '"'
    return cell  # terminal (UPPERCASE) or subrule (lowercase) — used as-is


def build_grammar(person_names: list[str], professions: list[str]) -> str:
    base = (GRAMMAR_DIR / "grammar_base.lark").read_text()

    rules = []
    for md_file in sorted(GRAMMAR_DIR.glob("T*.md")):
        content = md_file.read_text()
        header = next(
            (
                l
                for l in content.splitlines()
                if l.strip().startswith("|") and "---" not in l
            ),
            None,
        )
        if not header:
            continue
        cells = [c.strip() for c in header.split("|") if c.strip()]
        alias = md_file.stem.lower()
        tokens = " ".join(cell_to_lark(c) for c in cells)
        rules.append((tokens, alias))

    clue_lines = []
    for i, (tokens, alias) in enumerate(rules):
        prefix = "clue:" if i == 0 else "    |"
        clue_lines.append(f"{prefix} {tokens} -> {alias}")

    names_lower = [n.lower() for n in person_names]
    names_s = " | ".join(f'"{n}\'s"' for n in names_lower)
    names = " | ".join(f'"{n}"' for n in names_lower) + ' | "me"'
    jobs = " | ".join(
        f'"{p}" | "{p}s"' for p in sorted({p.lower() for p in professions})
    )

    return "\n".join(
        [
            "start: clue",
            "",
            *clue_lines,
            "",
            base,
            f"NAME_S: {names_s}",
            f"NAME: {names}",
            f"JOB: {jobs}",
        ]
    )


def load_parser(person_names: list[str], professions: list[str]) -> Lark:
    grammar = build_grammar(person_names, professions)
    return Lark(grammar, parser="earley", ambiguity="resolve", propagate_positions=True)


def preprocess_clue(clue: str) -> str:
    # Normalize non-breaking spaces, then lowercase
    return clue.replace("\u00a0", " ").lower()
