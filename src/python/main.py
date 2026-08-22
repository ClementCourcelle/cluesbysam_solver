import asyncio
import time

from lark import Lark, UnexpectedInput
from scraper import GameScraper
from grammar_loader import GRAMMAR_DIR, load_parser, preprocess_clue
from clue_types import Clue
from game_state import Row, Column, Status, Cell

import z3


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
        (l for l in content.splitlines() if l.strip().startswith("|") and "---" not in l),
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
            existing = [preprocess_clue(c.strip()) for c in line.split("|") if c.strip()]
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
    parser = load_parser([p for p in people.keys()], [p.profession for p in people.values()])
    seen_clues: set[str] = set()
    z3_grid = {(i, j): z3.Bool(f"c_{i} r_{j}") for i in Column.range() for j in Row.range()}
    print(z3_grid)
    solver = z3.Solver()
    known_inn = set()
    known_crim = set()
    new_inn = set()
    new_crim = set()

    # put first visible cell in known cells
    for p in people.values():
        if p.clue:
            c = Cell.id_to_coords(p.id)
            known_inn.add(c) if p.status == Status.INNOCENT else known_crim.add(c)
            break
    # add first visible persone to the solver
    solver.add(z3_grid[c[0], c[1]] == True)

    while True:
        # interpret new clues as z3 rules
        people = await GS.get_grid_state()
        new_clues = [n for n, person in people.items() if n not in seen_clues and person.clue]
        for name in new_clues:
            try:
                tree = parser.parse(preprocess_clue(people[name].clue)).children[0]
                print(tree.data)
            except UnexpectedInput:
                seen_clues.add(name)
                print(f"Not a clue: {people[name].clue}")
                continue
            clue_type = tree.data.upper()
            solver.add(Clue.types[clue_type](tree, name, people, z3_grid).get_rule())
            seen_clues.add(name)
        new_clues.clear()

        # test all unknown cells as criminal and innocent to find impossible cases
        for i in Column.range():
            for j in Row.range():
                tested_case = (i, j)
                if tested_case in known_inn.union(known_crim):
                    continue

                for is_inn in [True, False]:
                    solver.push()
                    solver.add(z3_grid[tested_case] == is_inn)
                    # print(self.solver)
                    if solver.check() == z3.sat:
                        solver.pop()
                        continue

                    # Contradiction => test_case is the opposite
                    if is_inn:
                        new_crim.add(tested_case)
                    else:
                        new_inn.add(tested_case)

                    solver.pop()

                    known_inn.update(new_inn)
                    known_crim.update(new_crim)
                    print(f"{new_inn = }")
                    print(f"{new_crim = }")
                    print(f"{known_inn = }")
                    print(f"{known_crim = }")
                    print("\n\n\n")

        if not new_inn and not new_crim:
            print("No solution found !")

        print("clicking \n")
        for i in new_inn:
            id = Cell.coords_to_id(i)
            await GS.mark_id(id, Status.INNOCENT)
            print(f"clicked {id} inn")
        new_inn.clear()

        for c in new_crim:
            id = Cell.coords_to_id(c)
            await GS.mark_id(id, Status.CRIMINAL)
            print(f"clicked {id} crim")
        new_crim.clear()

        if len(known_crim) + len(known_inn) == len(z3_grid):
            print("Done !")
            break
    time.sleep(30)


# async def load_new_indices() -> None:
#     GS = GameScraper(headless=False)
#     await GS.start()
#
#     people = await GS.get_grid_state()
#     parser = load_parser([p.name for p in people], [p.profession for p in people])
#     print(f"Loaded: {[p.name for p in people]}")
#     print(f"Jobs:   {sorted({p.profession for p in people})}")
#
#     seen_clues: set[str] = set()
#     round_num = 0
#
#     while True:
# clues = await GS.get_visible_clues()
#         new_clues = [c for c in clues if c not in seen_clues]
#
#         if new_clues:
#             round_num += 1
#             print(f"\n--- Round {round_num}: {len(new_clues)} new clue(s) ---")
#             for i, clue in enumerate(new_clues, len(seen_clues) + 1):
#                 parse_and_print_clue(parser, clue, i)
#                 seen_clues.add(clue)
#         else:
#             print("\n(no new clues)")
#
#         cmd = input("\nEnter to scan, 'r' to reload (new game), 'q' to quit: ").strip().lower()
#         if cmd == "q":
#             break
#         elif cmd == "r":
#             people = await GS.get_grid_state()
#             parser = load_parser([p.name for p in people], [p.profession for p in people])
#             seen_clues = set()
#             round_num = 0
#             professions = sorted({p.profession for p in people})
#             print(f"→ Reloaded: {[p.name for p in people]}")
#             print(f"   Jobs: {professions}")
#
#     await GS.stop()


if __name__ == "__main__":
    asyncio.run(main())
