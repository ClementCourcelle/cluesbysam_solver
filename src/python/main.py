import asyncio
from pathlib import Path

from lark import Lark, UnexpectedInput
from scraper import GameScraper

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
    names = " | ".join(f'"{n}"' for n in names_lower)
    jobs = " | ".join(f'"{p}"' for p in sorted({p.lower() for p in professions}))

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
    return clue.lower()


def node_to_text(node, preprocessed: str) -> str:
    from lark import Token

    if isinstance(node, Token):
        return str(node)
    try:
        return preprocessed[node.meta.start_pos : node.meta.end_pos]
    except AttributeError:
        return " ".join(node.scan_values(lambda _: True))


def record_clue_in_grammar(type_code: str, clue_tree, preprocessed: str) -> bool:
    """Append a new example row to the matching T*.md table (if not already present)."""
    file_path = GRAMMAR_DIR / f"{type_code}.md"
    if not file_path.exists():
        return False

    content = file_path.read_text()
    header_line = next(
        (
            l
            for l in content.splitlines()
            if l.strip().startswith("|") and "---" not in l
        ),
        None,
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
        elif child_idx < len(children):
            cells.append(node_to_text(children[child_idx], preprocessed))
            child_idx += 1
        else:
            cells.append("")

    new_row = "| " + " | ".join(cells) + " |"
    new_cells_norm = [preprocess_clue(c) for c in cells]

    for line in content.splitlines():
        if "|" in line and "---" not in line:
            existing = [
                preprocess_clue(c.strip()) for c in line.split("|") if c.strip()
            ]
            if existing == new_cells_norm:
                return False

    file_path.write_text(content.rstrip("\n") + "\n" + new_row + "\n")
    return True


def parse_and_print_clue(parser: Lark, raw_clue: str, index: int) -> None:
    preprocessed = preprocess_clue(raw_clue)
    print(f"[{index}] {raw_clue}")
    try:
        tree = parser.parse(preprocessed)
        clue_tree = tree.children[0]
        type_code = clue_tree.data.upper()
        added = record_clue_in_grammar(type_code, clue_tree, preprocessed)
        if added:
            print(f"     → ADDED TO {type_code}.md")
        else:
            print(f"     → {type_code}.md")
    except UnexpectedInput:
        print("     → ==> NO MATCH <==")


async def main() -> None:
    GS = GameScraper(headless=False)
    await GS.start()

    people = await GS.get_grid_state()
    parser = load_parser([p.name for p in people], [p.profession for p in people])

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
