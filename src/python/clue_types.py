from lark import Tree, Token
import z3
from itertools import combinations

from game_state import Cell, Row, Column, Status


class Clue:
    types = {}

    def __init_subclass__(cls):
        Clue.types[cls.__name__] = cls

    def __init__(self, tree: Tree, name: str, people: dict, grid: dict):
        var_names = []
        self.people = people
        self.grid = grid
        for c in tree.children:
            attr_name = Clue.get_available_name(var_names, c)
            var_names.append(attr_name)
            attr_val = Clue.get_value(c, name)
            setattr(self, attr_name, attr_val)

    @staticmethod
    def get_available_name(var_names: str, element: Tree | Token):
        """Return attribute name based on parsed type and existing attributes"""
        var_stem = "pos" if isinstance(element, Tree) else element.type.lower()
        var_stem = "nb" if var_stem == "no" else var_stem

        var_name = var_stem
        suffix = 2
        while var_name in var_names:
            var_name = var_stem + str(suffix)
            suffix += 1
        return var_name

    @staticmethod
    def get_value(element: Tree | Token, name: str):
        """Return attribute value based on parsed element type"""
        element = Clue.replace_me_values(element, name)
        if isinstance(element, Tree):
            return element
        if element.type == "AXIS":
            return Row if element.value == "row" else Column
        if element.type == "COORD":
            return (
                ord(element.value) - ord('a') + 1 if element.value.isalpha() else int(element.value)
            )
        if element.type == "NB":
            return 1 if element.value == "one" else int(element.value)
        if element.type == "NO":
            return 0
        return element.value

    @staticmethod
    def replace_me_values(node: Tree | Token, name: str) -> Tree | Token:
        """Iterate through tree to replace 'me, 'my', 'I' values"""
        if isinstance(node, Token):
            return Token(node.type, name) if node.value in ["me", "I", "my"] else node
        for i, child in enumerate(node.children):
            node.children[i] = Clue.replace_me_values(child, name)
        return node

    def dir_of_name(self, name: str, direction: str) -> list[tuple]:
        """Get the cells in a direction of a person"""
        return Cell.dir[direction](Cell.id_to_coords(self.people[name].id))

    def neighbors(self, name: str) -> list[tuple]:
        """Get cells neighboring of person"""
        return Cell.neighbors(Cell.id_to_coords(self.people[name].id))

    def name_to_cell(self, name: str) -> tuple:
        """Get cell coordinate of person"""
        return Cell.id_to_coords(self.people[name].id)

    def job_to_cells(self, job: str) -> list[tuple]:
        """Get cells of person with job"""
        return [Cell.id_to_coords(p.id) for p in self.people.values() if p.profession == job]

    def predicat(self, cell_indices: list[tuple], n: int, role=Status.INNOCENT):
        """Return rule to assign number of roles to a zone"""
        print(f"{cell_indices = }")
        print(f"{n = }")
        print(f"{role = }")
        cells = [self.grid[c[0], c[1]] for c in cell_indices]
        return (
            z3.Sum([z3.If(c, 1, 0) for c in cells]) == n
            if role == Status.INNOCENT
            else self.predicat(cell_indices, len(cells) - n)
        )

    def predicat_neq(self, cell_indices: list[tuple], n: int, role=Status.INNOCENT):
        """Return rule to forbid number of roles to a zone"""
        print(f"NON EQUAL")
        print(f"{cell_indices = }")
        print(f"{n = }")
        print(f"{role = }")
        cells = [self.grid[c[0], c[1]] for c in cell_indices]
        return (
            z3.Sum([z3.If(c, 1, 0) for c in cells]) != n
            if role == Status.INNOCENT
            else self.predicat_neq(cell_indices, len(cells) - n)
        )

    def predicat_less(self, cell_indices: list[tuple], n: int, role=Status.INNOCENT):
        """Return rule to assign maximum number of roles to a zone"""
        print(f"MORE")
        print(f"{cell_indices = }")
        print(f"{n = }")
        print(f"{role = }")
        cells = [self.grid[c[0], c[1]] for c in cell_indices]
        return (
            z3.Sum([z3.If(c, 1, 0) for c in cells]) < n
            if role == Status.INNOCENT
            else z3.Sum([z3.If(c, 1, 0) for c in cells]) >= len(cells) - n
        )

    def predicat_more_eq(self, cell_indices: list[tuple], n: int, role=Status.INNOCENT):
        """Return rule to assign minimum number of roles to a zone"""
        print(f"MORE")
        print(f"{cell_indices = }")
        print(f"{n = }")
        print(f"{role = }")
        cells = [self.grid[c[0], c[1]] for c in cell_indices]
        return (
            z3.Sum([z3.If(c, 1, 0) for c in cells]) >= n
            if role == Status.INNOCENT
            else z3.Sum([z3.If(c, 1, 0) for c in cells]) < len(cells) - n
        )

    def predicat_more_zone(
        self, cell_indices: list[tuple], cell_indices2: list[tuple], role: Status
    ):
        """Return rule to assign more roles in cells than cells2"""
        print(f"MORE")
        print(f"{cell_indices = }")
        print(f"{cell_indices2 = }")
        print(f"{role = }")
        cells = [self.grid[c[0], c[1]] for c in cell_indices]
        cells2 = [self.grid[c[0], c[1]] for c in cell_indices2]
        sum = (
            z3.Sum([z3.If(c, 1, 0) for c in cells])
            if role == Status.INNOCENT
            else z3.Sum([z3.If(c, 0, 1) for c in cells])
        )
        sum2 = (
            z3.Sum([z3.If(c, 1, 0) for c in cells2])
            if role == Status.INNOCENT
            else z3.Sum([z3.If(c, 0, 1) for c in cells2])
        )
        return sum > sum2

    def predicat_as_many(
        self, cell_indices: list[tuple], cell_indices2: list[tuple], role: Status, role2: Status
    ):
        """Return rule to assign as many roles in two zones"""
        print(f"AS MANY")
        print(f"{cell_indices = }")
        print(f"{cell_indices2 = }")
        print(f"{role = }")
        cells = [self.grid[c[0], c[1]] for c in cell_indices]
        cells2 = [self.grid[c[0], c[1]] for c in cell_indices2]
        sum = (
            z3.Sum([z3.If(c, 1, 0) for c in cells])
            if role == Status.INNOCENT
            else z3.Sum([z3.If(c, 0, 1) for c in cells])
        )
        sum2 = (
            z3.Sum([z3.If(c, 1, 0) for c in cells2])
            if role == Status.INNOCENT
            else z3.Sum([z3.If(c, 0, 1) for c in cells2])
        )
        return sum == sum2

    def split_roles_in_zone(self, zone, zone_role, role):
        """Return rule that assigns all the roles cells to to one part of a zone"""  # pire commentaire
        print("!! AND !!")
        return z3.And(
            self.predicat(zone_role, len(zone_role), role),
            self.predicat(zone, len(zone_role), role),
        )

    def or_range_predicat(self, cell_indices: list[tuple], range: range, role=Status.INNOCENT):
        """Return OR rules with range of possible number of roles"""  # 2e pire commentaire
        print("!! OR !!")
        return z3.Or([self.predicat(cell_indices, i, role) for i in range])

    def parity_in_zone(self, cell_indices: list[tuple], parity: str, role=Status.INNOCENT):
        """Return rules with possible role values based on parity"""  # 3e pire commentaire
        start = 0 if parity == 'even' else 1
        return self.or_range_predicat(cell_indices, range(start, len(cell_indices), 2), role)

    def pos_to_cells(self, pos: Tree) -> list[tuple]:
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
                    id = self.people[axis_tree.children[0]].id
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
                return self.neighbors(name)
            case 'in_between_names':
                id1 = self.people[pos.children[0].value].id
                id2 = self.people[pos.children[1].value].id
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
                return self.dir_of_name(name, dir)


class TA_1(Clue):
    def __init__(self, tree, name, people, grid):
        super().__init__(tree, name, people, grid)

    def get_rule(self):
        cells = self.pos_to_cells(self.pos)
        cells2 = self.pos_to_cells(self.pos2)
        inter = Cell.intersection(cells, cells2)
        print("!! AND !!")
        return z3.And(
            self.predicat(inter, self.nb, self.role), self.predicat(cells, self.nb2, self.role)
        )


class TA_2(Clue):
    def __init__(self, tree, name, people, grid):
        super().__init__(tree, name, people, grid)

    def get_rule(self):
        cells = self.pos_to_cells(self.pos)
        cells2 = self.pos_to_cells(self.pos2)
        inter = Cell.intersection(cells, cells2)

        return self.predicat(inter, self.nb, self.role)


class TB_1(Clue):
    def __init__(self, tree, name, people, grid):
        super().__init__(tree, name, people, grid)

    def get_rule(self):
        cells = self.pos_to_cells(self.pos)
        name_cell = self.name_to_cell(self.name)
        print("!! AND !!")
        return z3.And(
            self.predicat(cells, self.nb, self.role), self.predicat([name_cell], 1, self.role)
        )


class TB_2(Clue):
    def __init__(self, tree, name, people, grid):
        super().__init__(tree, name, people, grid)

    def get_rule(self):
        cells = self.neighbors(self.name2)
        name_cell = self.name_to_cell(self.name)
        print("!! AND !!")
        return z3.And(
            self.predicat(cells, self.nb, self.role), self.predicat([name_cell], 1, self.role)
        )


class TB_3(Clue):
    def __init__(self, tree, name, people, grid):
        super().__init__(tree, name, people, grid)

    def get_rule(self):
        cells = self.neighbors(self.name)
        return self.predicat(cells, self.nb, self.role)


class TC_1(Clue):
    def __init__(self, tree, name, people, grid):
        super().__init__(tree, name, people, grid)

    def get_rule(self):
        cells = self.pos_to_cells(self.pos)
        return self.predicat(cells, self.nb, self.role)


class TC_2(Clue):
    def __init__(self, tree, name, people, grid):
        super().__init__(tree, name, people, grid)

    def get_rule(self):
        cells = self.pos_to_cells(self.pos)
        return self.predicat_more_eq(cells, self.nb, self.role)


class TC_3(Clue):
    def __init__(self, tree, name, people, grid):
        super().__init__(tree, name, people, grid)

    def get_rule(self):
        cells = self.axis.cells(self.coord)
        cells2 = self.axis.cells(self.coord2)
        return self.predicat_more_zone(cells, cells2, self.role)


class TD_1(Clue):
    def __init__(self, tree, name, people, grid):
        super().__init__(tree, name, people, grid)

    def get_rule(self):
        print("!! AND !!")
        return z3.And(
            [
                self.predicat_more_eq(self.axis.cells(ax_coord), self.nb, self.role)
                for ax_coord in self.axis.range()
            ]
        )


class TD_2(Clue):
    def __init__(self, tree, name, people, grid):
        super().__init__(tree, name, people, grid)

    def get_rule(self):
        print("!! AND !!")
        return z3.Or(
            [
                z3.And(
                    [self.predicat(self.axis.cells(ax_coord), self.nb, self.role)]
                    + [
                        self.predicat_neq(self.axis.cells(others), self.nb, self.role)
                        for others in self.axis.range()
                        if others != ax_coord
                    ]
                )
                for ax_coord in self.axis.range()
            ]
        )


class TD_3(Clue):
    def __init__(self, tree, name, people, grid):
        super().__init__(tree, name, people, grid)

    def get_rule(self):
        print("!! AND !!")
        return z3.And(
            [self.predicat(self.axis.cells(self.coord), self.nb, self.role)]
            + [
                self.predicat_neq(self.axis.cells(ax_coord), self.nb, self.role)
                for ax_coord in self.axis.range()
                if ax_coord != self.coord
            ]
        )


class TE_3(Clue):
    def __init__(self, tree, name, people, grid):
        super().__init__(tree, name, people, grid)

    def get_rule(self):
        print(f"{self.job = }")
        print(f"{self.job2 = }")
        cells = self.job_to_cells(self.job)
        cells2 = self.job_to_cells(self.job2)
        return self.predicat_as_many(cells, cells2, self.role, self.role2)


class TMP_4(Clue):
    def __init__(self, tree, name, people, grid):
        super().__init__(tree, name, people, grid)

    def get_rule(self):
        cells = self.neighbors(self.name)
        cells2 = self.pos_to_cells(self.pos)
        inter = Cell.intersection(cells, cells2)
        return self.parity_in_zone(inter, self.parity, self.role)


class TMP_6(Clue):
    def __init__(self, tree, name, people, grid):
        super().__init__(tree, name, people, grid)

    def get_rule(self):
        cells = self.pos_to_cells(self.pos)
        return self.parity_in_zone(cells, self.parity, self.role)


class TMP_7(Clue):
    def __init__(self, tree, name, people, grid):
        super().__init__(tree, name, people, grid)

    def get_rule(self):
        pos_cells = self.pos_to_cells(self.pos)
        if self.allboth == "both":
            cells_groups = Cell.n_connected(pos_cells, 2)
        else:
            cells_groups = Cell.any_connected(pos_cells)

        print("OR!!!")
        return z3.Or(
            [self.split_roles_in_zone(pos_cells, group, self.role) for group in cells_groups]
        )


class TMP_11(Clue):
    def __init__(self, tree, name, people, grid):
        super().__init__(tree, name, people, grid)

    def get_rule(self):
        cells = self.job_to_cells(self.job)
        zone_dir = list(Cell.zone_directly_dir(cells, self.dir).values())
        return self.predicat(zone_dir, self.nb, self.role)


class TMP_18(Clue):
    def __init__(self, tree, name, people, grid):
        super().__init__(tree, name, people, grid)

    def get_rule(self):
        cells = self.pos_to_cells(self.pos)
        zone_dir = list(Cell.zone_directly_dir(cells, self.dir).values())
        return self.predicat(zone_dir, self.nb, self.role)


class TMP_19(Clue):
    def __init__(self, tree, name, people, grid):
        super().__init__(tree, name, people, grid)

    def get_rule(self):
        cells = self.pos_to_cells(self.pos)
        # zone_dir = list(Cell.zone_directly_dir(cells, self.dir).values())
        zone_dir = Cell.zone_directly_dir(cells, self.dir)
        combs = list(combinations(list(zone_dir.items()), self.nb))

        return z3.Or(
            [
                z3.And(
                    [
                        z3.And(
                            self.predicat([pair[0]], 1, self.role),
                            self.predicat([pair[1]], 1, self.role2),
                        )
                        for pair in comb
                    ]
                    + [
                        z3.Or(
                            self.predicat_neq([pair[0]], 1, self.role),
                            self.predicat_neq([pair[1]], 1, self.role2),
                        )
                        for pair in list(zone_dir.items())
                        if pair not in comb
                    ]
                )
                for comb in combs
            ]
        )


class TMP_23(Clue):
    def __init__(self, tree, name, people, grid):
        super().__init__(tree, name, people, grid)

    def get_rule(self):
        cells = self.pos_to_cells(self.pos)
        neighbors = [Cell.neighbors(c) for c in cells]
        combs = list(combinations(neighbors, self.nb))
        print(f"{cells = }")
        print(f"{neighbors = }")
        print(f"{combs = }")
        print(f"{self.nb = }")
        print(f"{self.nb2 = }")
        return z3.Or(
            [
                z3.And(
                    [self.predicat(n, self.nb2, self.role) for n in neighbors if n in comb]
                    + [
                        self.predicat_neq(n, self.nb2, self.role)
                        for n in neighbors
                        if n not in comb
                    ]
                )
                for comb in combs
            ]
        )
