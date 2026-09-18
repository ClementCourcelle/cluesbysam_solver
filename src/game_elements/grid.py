from lark import Tree

NB_ROWS = 5
NB_COLS = 4


class Cell:
    people = None

    @staticmethod
    def id_to_coords(id: str) -> tuple:
        """Convert person id in cell coordinates"""
        return (ord(id[0].upper()) - ord('A') + 1, int(id[1]))

    @staticmethod
    def coords_to_id(coords: tuple) -> str:
        """Convert cell coordinates to person id"""
        return f"{chr(ord('A') + coords[0] - 1)}{coords[1]}"

    @staticmethod
    def dir_of_name(name: str, direction: str) -> list[tuple]:
        """Get the cells in a direction of a person"""
        return Cell.dir[direction](Cell.id_to_coords(Cell.people[name].id))

    @staticmethod
    def neighbors(name: str) -> list[tuple]:
        """Get cells neighboring of person"""
        return Cell.neighbors_from_coords(Cell.id_to_coords(Cell.people[name].id))

    @staticmethod
    def name_to_cell(name: str) -> tuple:
        """Get cell coordinate of person"""
        return Cell.id_to_coords(Cell.people[name].id)

    @staticmethod
    def job_to_cells(job: str) -> list[tuple]:
        """Get cells of person with job"""
        return [Cell.id_to_coords(p.id) for p in Cell.people.values() if p.profession == job]

    @staticmethod
    def pos_to_cells(pos: Tree) -> list[tuple]:
        """Get cells from position tree"""
        type = pos.data
        print(pos)
        match (type):
            case 'in_axis':
                axis_tree = pos.children[0]
                if axis_tree.children[0].type == "AXIS":
                    axis_type = Row if axis_tree.children[0].value == "row" else Column
                    value = axis_tree.children[1].value
                else:
                    id = Cell.people[axis_tree.children[0]].id
                    if axis_tree.children[1].value == "row":
                        axis_type = Row
                        value = id[1]
                    else:
                        axis_type = Column
                        value = id[0]
                axis_coord = ord(value) - ord('a') + 1 if value.isalpha() else int(value)
                print(f"{axis_coord = }")
                return axis_type.cells(axis_coord)
            case 'on_the_edges':
                return Cell.edges()
            case 'in_a_corner':
                return Cell.corners()
            case 'neighboring_name':
                name = pos.children[0].value
                return Cell.neighbors(name)
            case 'in_between_names':
                id1 = Cell.people[pos.children[0].value].id
                id2 = Cell.people[pos.children[1].value].id
                vertical = Cell.id_to_coords(id1)[0] == Cell.id_to_coords(id2)[0]

                first = Cell.id_to_coords(id1 if id1 < id2 else id2)
                sec = Cell.id_to_coords(id1 if first == id1 else id2)

                return (
                    Cell.intersection(Cell.below(first), Cell.above(sec))
                    if vertical
                    else Cell.intersection(Cell.right(first), Cell.left(sec))
                )
            case 'dir_of_name':
                dir = pos.children[0].value
                name = pos.children[1].value
                return Cell.dir_of_name(name, dir)

    @staticmethod
    def all_cells() -> list[tuple]:
        """Get all cells in the grid"""
        return [(i, j) for i in Column.range() for j in Row.range()]

    @staticmethod
    def neighbors_from_coords(coords: str) -> list[tuple]:
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
    def zone_directly_dir(cells: list[tuple], dir: str) -> dict[tuple, tuple]:
        """Get cells directly on the direction of input cells"""
        zone = {}
        print("ZONE !!!")
        print(f"{cells = }")
        for c in cells:
            dir_of_cell = Cell.dir[dir](c)
            print(f"{c = }")
            print(f"{dir_of_cell = }")
            if not dir_of_cell:
                continue

            zone[c] = next(x for x in dir_of_cell if abs(c[0] - x[0] + c[1] - x[1]) == 1)
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
