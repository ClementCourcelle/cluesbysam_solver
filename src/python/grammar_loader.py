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
    base += (GRAMMAR_DIR / "clue_types.lark").read_text()

    names_lower = [n.lower() for n in person_names]
    # names_s = " | ".join(f'"{n}\'s"' for n in names_lower)
    names = " | ".join(f'"{n}"' for n in names_lower) + ' | "me" | "i"'
    jobs = " | ".join(f'"{p}"' for p in sorted({p.lower() for p in professions}))

    return "\n".join(
        [
            base,
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
