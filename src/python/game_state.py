from enum import Enum
from typing import List, Optional
from pydantic import BaseModel

NB_ROWS = 5
NB_COLS = 4


class Cell:

    @staticmethod
    def id_to_coords(id):
        return (ord(id[0].upper()) - ord('A') + 1, int(id[1]))

    @staticmethod
    def coords_to_id(coords):
        return f"{chr(ord('A') + coords[0] - 1)}{coords[1]}"

    @staticmethod
    def neighbors(id):
        coords = Cell.id_to_coords(id)
        return [
            (i, j)
            for i in range(coords[0] - 1, coords[0] + 2)
            for j in range(coords[1] - 1, coords[1] + 2)
            if (i in range(1, NB_COLS + 1) and j in range(1, NB_ROWS + 1) and (i, j) != coords)
        ]

    @staticmethod
    def above(id):
        coords = Cell.id_to_coords(id)
        return [(coords[0], i) for i in range(1, coords[1])]

    @staticmethod
    def below(id):
        coords = Cell.id_to_coords(id)
        return [(coords[0], i) for i in range(coords[1], NB_ROWS + 1)]

    @staticmethod
    def left(id):
        coords = Cell.id_to_coords(id)
        return [(i, coords[1]) for i in range(1, coords[0])]

    @staticmethod
    def right(id):
        coords = Cell.id_to_coords(id)
        return [(i, coords[1]) for i in range(coords[0], NB_COLS + 1)]

    @staticmethod
    def corners():
        return [(1, 1), (1, NB_COLS), (NB_ROWS, 1), (NB_ROWS, NB_COLS)]

    @staticmethod
    def edges():
        return [
            (i, j)
            for i in range(1, NB_COLS + 1)
            for j in range(1, NB_ROWS + 1)
            if i in [1, NB_COLS] or j in [1, NB_ROWS]
        ]

    @staticmethod
    def intersection(cells: list[tuple], cells2: list[tuple]):
        return list(set(cells) & set(cells2))

    @staticmethod
    def n_connected(cells: list, n):
        # find direction
        ind = 1 if cells[0][0] == cells[1][0] else 0
        cells.sort(key=lambda cell: cell[ind])
        return [
            [cells[i] for i in range(start, start + n)]
            for start in range(cells[0][ind] - 1, cells[-1][ind] - n + 1)
        ]

    @staticmethod
    def any_connected(cells: list):
        res = []
        for i in range(1, len(cells) + 1):
            res += Cell.n_connected(cells, i)
        return res

    # axis = {'row': row, 'column': column}
    dir = {'above': above, 'below': below, 'right': right, 'left': left}


def range_axis(axis):
    return range(1, NB_COLS + 1) if axis == 'column' else range(1, NB_ROWS + 1)


class Row:

    N = NB_ROWS
    N_ELEMS = NB_COLS

    @staticmethod
    def range():
        return range(1, Row.N + 1)

    @staticmethod
    def range_elems():
        return range(1, Row.N_ELEMS + 1)

    @staticmethod
    def cells(coord: int):
        return [(i, coord) for i in Row.range_elems()]


class Column:

    N = NB_COLS
    N_ELEMS = NB_ROWS

    @staticmethod
    def range():
        return range(1, Column.N + 1)

    @staticmethod
    def range_elems():
        return range(1, Column.N_ELEMS + 1)

    @staticmethod
    def cells(coord: int):
        return [(coord, i) for i in Column.range_elems()]


class Status(str, Enum):
    UNKNOWN = "unknown"
    INNOCENT = "innocent"
    CRIMINAL = "criminal"


class Person(BaseModel):
    id: str  # "A1"
    name: str
    profession: str
    # row: int  # 1-5
    # col: str  # A-D
    status: Status = Status.UNKNOWN
    clue: Optional[str] = None  # The clue revealed by this person, if any
    # neighbors: List[str] = []  # Names of neighboring people


class GameState(BaseModel):
    people: List[Person]
    active_clues: List[str]
