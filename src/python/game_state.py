from enum import Enum
from typing import List, Optional
from pydantic import BaseModel

NB_ROWS = 5
NB_COLS = 4


class Cell:

    @staticmethod
    def id_to_coords(id: str) -> tuple:
        """Convert person id in cell coordinates"""
        return (ord(id[0].upper()) - ord('A') + 1, int(id[1]))

    @staticmethod
    def coords_to_id(coords: tuple) -> str:
        """Convert cell coordinates to person id"""
        return f"{chr(ord('A') + coords[0] - 1)}{coords[1]}"

    @staticmethod
    def neighbors(coords: str) -> list[tuple]:
        """Get coordinates of cells neighboring a cell"""
        return [
            (i, j)
            for i in range(coords[0] - 1, coords[0] + 2)
            for j in range(coords[1] - 1, coords[1] + 2)
            if (i in range(1, NB_COLS + 1) and j in range(1, NB_ROWS + 1) and (i, j) != coords)
        ]

    @staticmethod
    def above(coords: tuple) -> list[tuple]:
        """Get cells above input cell"""
        return [(coords[0], i) for i in range(1, coords[1])]

    @staticmethod
    def below(coords: tuple) -> list[tuple]:
        """Get cells below input cell"""
        return [(coords[0], i) for i in range(coords[1] + 1, NB_ROWS + 1)]

    @staticmethod
    def left(coords: tuple) -> list[tuple]:
        """Get cells left of input cell"""
        return [(i, coords[1]) for i in range(1, coords[0])]

    @staticmethod
    def right(coords: tuple) -> list[tuple]:
        """Get cells right of input cell"""
        return [(i, coords[1]) for i in range(coords[0] + 1, NB_COLS + 1)]

    @staticmethod
    def corners() -> list[tuple]:
        """Get cells in the corners of the grid"""
        return [(1, 1), (1, NB_ROWS), (NB_COLS, 1), (NB_COLS, NB_ROWS)]

    @staticmethod
    def edges() -> list[tuple]:
        """Get cells on the edges of the grid"""
        return [
            (i, j)
            for i in range(1, NB_COLS + 1)
            for j in range(1, NB_ROWS + 1)
            if i in [1, NB_COLS] or j in [1, NB_ROWS]
        ]

    @staticmethod
    def zone_directly_dir(cells: list[tuple], dir: str) -> list[tuple]:
        """Get cells directly on the direction of input cells"""
        zone = []
        print("ZONE !!!")
        print(f"{cells = }")
        for c in cells:
            dir_of_cell = Cell.dir[dir](c)
            print(f"{c = }")
            print(f"{dir_of_cell = }")
            if not dir_of_cell:
                continue

            zone.append(next(x for x in dir_of_cell if abs(c[0] - x[0] + c[1] - x[1]) == 1))
        return zone

    @staticmethod
    def intersection(cells: list[tuple], cells2: list[tuple]) -> list[tuple]:
        """Get the intersectoin of two cell lists"""
        return list(set(cells) & set(cells2))

    @staticmethod
    def n_connected(cells: list, n) -> list[list[tuple]]:
        """Find the possible combinations of n cells connected to each other inside a zone"""
        # find direction
        ind = 1 if cells[0][0] == cells[1][0] else 0
        cells.sort(key=lambda cell: cell[ind])
        return [
            [cells[i] for i in range(start, start + n)]
            for start in range(cells[0][ind] - 1, cells[-1][ind] - n + 1)
        ]

    @staticmethod
    def any_connected(cells: list[tuple]) -> list[list[tuple]]:
        """Find all the possible combinations of cells connected to each other inside a zone"""
        res = []
        for i in range(1, len(cells) + 1):
            res += Cell.n_connected(cells, i)
        return res

    dir = {'above': above, 'below': below, 'right': right, 'left': left}


class Row:

    N = NB_ROWS
    N_ELEMS = NB_COLS

    @staticmethod
    def range() -> range:
        """Get range of possible row values"""
        return range(1, Row.N + 1)

    @staticmethod
    def range_elems() -> range:
        """Get range of possible elements in a row"""
        return range(1, Row.N_ELEMS + 1)

    @staticmethod
    def cells(coord: int) -> list[tuple]:
        """Get all cells in one row"""
        return [(i, coord) for i in Row.range_elems()]


class Column:

    N = NB_COLS
    N_ELEMS = NB_ROWS

    @staticmethod
    def range() -> range:
        """Get range of possible column values"""
        return range(1, Column.N + 1)

    @staticmethod
    def range_elems() -> range:
        """Get range of possible elements in a column"""
        return range(1, Column.N_ELEMS + 1)

    @staticmethod
    def cells(coord: int) -> list[tuple]:
        """Get all cells in one column"""
        return [(coord, i) for i in Column.range_elems()]


class Status(str, Enum):
    UNKNOWN = "unknown"
    INNOCENT = "innocent"
    CRIMINAL = "criminal"


class Person(BaseModel):
    id: str  # "A1"
    name: str
    profession: str
    status: Status = Status.UNKNOWN
    clue: Optional[str] = None  # The clue revealed by this person, if any


class GameState(BaseModel):
    people: List[Person]
    active_clues: List[str]
