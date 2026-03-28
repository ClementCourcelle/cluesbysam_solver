import asyncio
import re
from pathlib import Path

from lark import Lark, UnexpectedInput
from scraper import GameScraper

GRAMMAR_PATH = Path(__file__).parent.parent.parent / "config" / "grammar.lark"
GRAMMAR_DIR = Path(__file__).parent.parent.parent / "grammar"


def load_parser(person_names: list[str], professions: list[str]) -> Lark:
    grammar_template = GRAMMAR_PATH.read_text()

    names_lower = [n.lower() for n in person_names]
    names_s = " | ".join(f'"{n}\'s"' for n in names_lower)
    names = " | ".join(f'"{n}"' for n in names_lower)

    professions_lower = sorted({p.lower() for p in professions})
    jobs = " | ".join(f'"{p}"' for p in professions_lower)

    injected = f"NAME_S: {names_s}\nNAME: {names}\nJOB: {jobs}\n"
    grammar = grammar_template + injected

    return Lark(grammar, parser="earley", ambiguity="resolve", propagate_positions=True)


def preprocess_clue(clue: str) -> str:
    text = clue.lower()

    # Normalize contractions
    text = text.replace("there's", "there is")

    # Normalize plurals
    text = text.replace("neighbors", "neighbor")
    text = text.replace("innocents", "innocent")
    text = text.replace("criminals", "criminal")

    # Remove "exactly" or "only" directly before a number
    text = re.sub(r"\b(exactly|only)\s+([1-9][0-9]*)", r"\2", text)

    return text


def type_code_from_alias(alias: str) -> str | None:
    # Example : 'ta_1_nb_of_...' -> 'TA_1'
    m = re.match(r"^(t[a-z]_\d+)_", alias)
    return m.group(1).upper() if m else None


def node_to_text(node, preprocessed: str) -> str:
    """Return the substring of preprocessed that this tree node matched."""
    from lark import Token

    if isinstance(node, Token):
        return str(node)
    try:
        return preprocessed[node.meta.start_pos : node.meta.end_pos]
    except AttributeError:
        # Fallback: join all terminal values
        return " ".join(node.scan_values(lambda _: True))


def record_clue_in_grammar(
    type_code: str, raw_clue: str, clue_tree, preprocessed: str
) -> bool:
    file_path = GRAMMAR_DIR / f"{type_code}.md"
    if not file_path.exists():
        return False

    content = file_path.read_text()

    header_line = next(
        (l for l in content.splitlines() if l.strip().startswith("|")), None
    )
    if not header_line:
        return False

    col_headers = [c.strip() for c in header_line.split("|") if c.strip()]
    children = list(clue_tree.children)
    child_idx = 0
    cells = []

    for header in col_headers:
        if header.startswith('"') and header.endswith('"'):
            cells.append(header[1:-1])
        else:
            if child_idx < len(children):
                cells.append(node_to_text(children[child_idx], preprocessed))
                child_idx += 1
            else:
                cells.append("")

    new_row = "| " + " | ".join(cells) + " |"

    new_cells_norm = [preprocess_clue(c) for c in cells]
    for line in content.splitlines():
        if "|" in line and "---" not in line:
            existing_cells = [preprocess_clue(c) for c in line.split("|") if c.strip()]
            if existing_cells == new_cells_norm:
                return False

    file_path.write_text(content.rstrip("\n") + "\n" + new_row + "\n")
    return True


def parse_and_print_clue(parser: Lark, raw_clue: str, index: int) -> None:
    preprocessed = preprocess_clue(raw_clue)
    print(f"[{index}] {raw_clue}")
    print(f"     → {preprocessed}")
    try:
        tree = parser.parse(preprocessed)
        clue_tree = tree.children[0]
        alias = clue_tree.data
        print(f"     OK: {alias}")
        type_code = type_code_from_alias(alias)
        if type_code:
            added = record_clue_in_grammar(type_code, raw_clue, clue_tree, preprocessed)
            if added:
                print(f"     → ajouté dans {type_code}.md")
            elif added is False:
                print(f"     → déjà présent dans {type_code}.md")
    except UnexpectedInput as e:
        print(f"     ERROR: {e}")


async def main():
    GS = GameScraper(headless=False)
    await GS.start()

    people = await GS.get_grid_state()
    person_names = [p.name for p in people]
    professions = [p.profession for p in people]
    parser = load_parser(person_names, professions)

    seen_clues: set[str] = set()
    round_num = 0

    while True:
        clues = await GS.get_visible_clues()
        new_clues = [c for c in clues if c not in seen_clues]

        if new_clues:
            round_num += 1
            print(f"\n--- Round {round_num}: {len(new_clues)} new clue(s) ---")
            for i, clue in enumerate(new_clues, len(seen_clues) + 1):
                parse_and_print_clue(parser, clue, i)
                seen_clues.add(clue)
        else:
            print("\n(no new clues)")

        cmd = input("\nPress Enter to scan again, or 'q' to quit: ").strip().lower()
        if cmd == "q":
            break

    await GS.stop()


if __name__ == "__main__":
    asyncio.run(main())
