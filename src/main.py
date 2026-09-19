import asyncio
import time
from sortedcontainers import SortedSet

from lark import UnexpectedInput
import z3
import click

from utils import GameScraper
from grammar import load_parser, preprocess_clue
from interpreter.clue_types import Clue
from interpreter.constraints import Constraint
from game_elements import Row, Column, Status, Cell


async def solve(interrupt: bool) -> None:
    GS = GameScraper(headless=False)
    await GS.start()

    people = await GS.get_grid_state()
    Cell.people = people
    parser = load_parser([p for p in people.keys()], [p.profession for p in people.values()])
    seen_clues: set[str] = set()
    z3_grid = {(i, j): z3.Bool(f"c_{i} r_{j}") for i in Column.range() for j in Row.range()}
    Constraint.grid = z3_grid
    solver = z3.Solver()
    known_cells = SortedSet()
    new_inn = set()
    new_crim = set()

    # put first visible cell in known cells and add rule to solver
    for p in people.values():
        if p.clue:
            c = Cell.id_to_coords(p.id)
            known_cells.add(c)
            solver.add(z3_grid[c[0], c[1]] == True if p.status == Status.INNOCENT else False)
            break

    while True:
        # interpret new clues as z3 rules
        people = await GS.get_grid_state()
        new_clues = [n for n, person in people.items() if n not in seen_clues and person.clue]
        for name in new_clues:
            try:
                print(f"{people[name].id} : {people[name].clue}")
                tree = parser.parse(preprocess_clue(people[name].clue)).children[0]
                print(tree.data)
            except UnexpectedInput:
                seen_clues.add(name)
                print(f"Not a clue: {people[name].clue}")
                continue
            clue_type = tree.data.upper()
            solver.add(Clue.types[clue_type](tree, name).get_rule())
            seen_clues.add(name)
        new_clues.clear()

        # test all unknown cells as criminal and innocent to find impossible cases
        for i in Column.range():
            for j in Row.range():
                tested_case = (i, j)
                if tested_case in known_cells:
                    continue

                for is_inn in [True, False]:
                    solver.push()
                    solver.add(z3_grid[tested_case] == is_inn)
                    if solver.check() == z3.sat:
                        solver.pop()
                        continue

                    # Contradiction => test_case is the opposite
                    if is_inn:
                        new_crim.add(tested_case)
                    else:
                        new_inn.add(tested_case)

                    solver.pop()

                    known_cells.update(new_inn)
                    known_cells.update(new_crim)
                    print(f"{new_inn = }")
                    print(f"{new_crim = }")

        if not new_inn and not new_crim:
            print("No solution found !")
            break

        if interrupt and len(known_cells) == len(z3_grid):
            print(
                f"\nInterrupting before completion.\n"
                f"Last innocents: {new_inn if new_inn else ""}\n"
                f"Last criminals: {new_crim if new_crim else ""}"
            )
            break

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

        if len(known_cells) == len(z3_grid):
            print("Puzzle solved !")
            break

    await GS.user_stop()


@click.command()
@click.option(
    "--interrupt", '-i', is_flag=True, help="Ends before completing last step of the puzzle."
)
def main(interrupt):
    asyncio.run(solve(interrupt))


if __name__ == "__main__":
    main()
