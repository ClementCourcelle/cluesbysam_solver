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


class GameEngine:
    def __init__(self, interrupt: bool):
        self.interrupt = interrupt
        self.GS = GameScraper(headless=False)
        self.solver = z3.Solver()
        self.known_cells = SortedSet()
        self.seen_clues = set()
        self.solved = False
        self.z3_grid = {
            (i, j): z3.Bool(f"c_{i} r_{j}") for i in Column.range() for j in Row.range()
        }
        Constraint.grid = self.z3_grid

    async def solve(self):
        await self.GS.start()
        self.people = await self.GS.get_grid_state()
        self.parser = load_parser(
            [p for p in self.people.keys()], [p.profession for p in self.people.values()]
        )
        Cell.people = self.people

        # put first visible cell in known cells and add rule to solver
        for p in self.people.values():
            if p.status != Status.UNKNOWN:
                c = Cell.id_to_coords(p.id)
                self.known_cells.add(c)
                self.solver.add(
                    self.z3_grid[c[0], c[1]] == True if p.status == Status.INNOCENT else False
                )
                break
        await self.game_loop()

    async def get_new_clues(self):
        self.people = await self.GS.get_grid_state()
        new_clues = [
            n for n, person in self.people.items() if n not in self.seen_clues and person.clue
        ]
        for name in new_clues:
            try:
                print(f"{self.people[name].id} : {self.people[name].clue}")
                tree = self.parser.parse(preprocess_clue(self.people[name].clue)).children[0]
                print(tree.data)
            except UnexpectedInput:
                self.seen_clues.add(name)
                print(f"Not a clue: {self.people[name].clue}")
                continue
            clue_type = tree.data.upper()
            self.solver.add(Clue.types[clue_type](tree, name).get_rule())
            self.seen_clues.add(name)

    async def find_new_status(self):
        # test all unknown cells as criminal and innocent to find impossible cases
        new_inn = set()
        new_crim = set()
        for i in Column.range():
            for j in Row.range():
                tested_case = (i, j)
                if tested_case in self.known_cells:
                    continue

                for is_inn in [True, False]:
                    self.solver.push()
                    self.solver.add(self.z3_grid[tested_case] == is_inn)
                    if self.solver.check() == z3.sat:
                        self.solver.pop()
                        continue

                    # Contradiction => test_case is the opposite
                    if is_inn:
                        new_crim.add(tested_case)
                    else:
                        new_inn.add(tested_case)

                    self.solver.pop()

                    self.known_cells.update(new_inn)
                    self.known_cells.update(new_crim)
        return (new_inn, new_crim)
        print(f"{new_inn = }")
        print(f"{new_crim = }")

    async def mark_new_people(self, new_inn, new_crim):
        for i in new_inn:
            id = Cell.coords_to_id(i)
            await self.GS.mark_id(id, Status.INNOCENT)
            print(f"clicked {id} inn")

        for c in new_crim:
            id = Cell.coords_to_id(c)
            await self.GS.mark_id(id, Status.CRIMINAL)
            print(f"clicked {id} crim")

    async def game_loop(self):
        while not self.solved:
            await self.get_new_clues()
            new_inn, new_crim = await self.find_new_status()

            if not new_inn and not new_crim:
                print("No solution found !")
                break

            if self.interrupt and len(self.known_cells) == len(self.z3_grid):
                print(
                    f"\nInterrupting before completion.\n"
                    f"Last innocents: {new_inn if new_inn else ""}\n"
                    f"Last criminals: {new_crim if new_crim else ""}"
                )
                break

            await self.mark_new_people(new_inn, new_crim)

            if len(self.known_cells) == len(self.z3_grid):
                self.solved = True
                print("Puzzle solved !")

        await self.GS.user_stop()


async def start(interrupt: bool) -> None:
    engine = GameEngine(interrupt)
    await engine.solve()


@click.command()
@click.option(
    "--interrupt", '-i', is_flag=True, help="Ends before completing last step of the puzzle."
)
def main(interrupt):
    asyncio.run(start(interrupt))


if __name__ == "__main__":
    main()
