from lark import Tree, Token
from game_state import Cell, Row, Column, Status
import z3


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

    def neighbors(self, name) -> list[tuple]:
        """Get cells neighboring of person"""
        return Cell.neighbors(self.people[name].id)

    def name_to_cell(self, name) -> tuple:
        """Get cell coordinate of person"""
        return Cell.id_to_coords(self.people[name].id)

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

    def pos_to_cells(self, pos: Tree) -> list[Cell]:
        """Get cells from position tree"""
        type = pos.data
        match (type):
            case 'in_axis':
                axis_type = Row if pos.children[0].value == "row" else Column
                value = pos.children[1].value
                axis_coord = ord(value) - ord('a') + 1 if value.isalpha() else int(value)
                print(f"{axis_coord = }")
                return axis_type.cells(axis_coord)
            case 'on_the_edges':
                return Cell.edges()
            case 'in_a_corner':
                return Cell.corners()
            case 'neighboring_name':
                name = pos.children[0].value
                return Cell.neighbors(self.people[name].id)
            case 'in_between_names':
                id1 = self.people[pos.children[0].value].id
                id2 = self.people[pos.children[1].value].id
                vertical = Cell.id_to_coords(id1)[0] == Cell.id_to_coords(id2)[0]

                first = id1 if id1 < id2 else id2
                sec = id1 if first == id1 else id2

                return (
                    Cell.below(first) and Cell.above(sec)
                    if vertical
                    else Cell.right(first) and Cell.left(sec)
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


class TMP_18(Clue):
    def __init__(self, tree, name, people, grid):
        super().__init__(tree, name, people, grid)

    def get_rule(self):
        cells = self.pos_to_cells(self.pos)
        return self.predicat(Cell.zone_directly_dir(cells, self.dir), self.nb, self.role)
