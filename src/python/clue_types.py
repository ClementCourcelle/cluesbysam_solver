from lark import Tree, Token
from game_state import Cell, Row, Column
import z3


class Clue:
    types = {}

    def __init_subclass__(cls):
        Clue.types[cls.__name__] = cls

    def __init__(self, tree, name, people, grid):
        var_names = []
        self.people = people
        self.grid = grid
        for c in tree.children:
            attr_name = Clue.get_available_name(var_names, c)
            var_names.append(attr_name)
            attr_val = Clue.get_value(c, name)
            setattr(self, attr_name, attr_val)

    @staticmethod
    def get_available_name(var_names, element):
        var_stem = "pos" if isinstance(element, Tree) else element.type.lower()
        var_stem = "nb" if var_stem == "no" else var_stem

        var_name = var_stem
        suffix = 2
        while var_name in var_names:
            var_name = var_stem + str(suffix)
            suffix += 1
        return var_name

    @staticmethod
    def get_value(element, name):
        element = Clue.replace_me_values(element, name)
        if isinstance(element, Tree):
            return element
        if element.type == "NB":
            return 1 if element.value == "one" else int(element.value)
        if element.type == "NO":
            return 0
        if element.type == "AXIS":
            return Row if element.value == "row" else Column
        if element.type == "COORD":
            return ord(value) - ord('a') + 1 if value.isalpha() else int(value)
        value = element.value
        if value in ["me", "I"]:
            value = name
        return value

    def neighbors(self, name):
        return Cell.neighbors(self.people[name].id)

    def name_to_cell(self, name):
        return Cell.id_to_coords(self.people[name].id)

    def predicat(self, cell_indices: list[tuple], n: int, role='innocent'):
        print(f"{cell_indices = }")
        print(f"{n = }")
        print(f"{role = }")
        cells = [self.grid[c[0], c[1]] for c in cell_indices]
        return (
            z3.Sum([z3.If(c, 1, 0) for c in cells]) == n
            if role == 'innocent'
            else self.predicat(cell_indices, len(cells) - n)
        )

    def predicat_less(self, cell_indices: list[tuple], n: int, role='innocent'):
        print(f"MORE")
        print(f"{cell_indices = }")
        print(f"{n = }")
        print(f"{role = }")
        cells = [self.grid[c[0], c[1]] for c in cell_indices]
        return (
            z3.Sum([z3.If(c, 1, 0) for c in cells]) < n
            if role == 'innocent'
            else z3.Sum([z3.If(c, 1, 0) for c in cells]) >= len(cells) - n
        )

    def predicat_more_eq(self, cell_indices: list[tuple], n: int, role='innocent'):
        print(f"MORE")
        print(f"{cell_indices = }")
        print(f"{n = }")
        print(f"{role = }")
        cells = [self.grid[c[0], c[1]] for c in cell_indices]
        return (
            z3.Sum([z3.If(c, 1, 0) for c in cells]) >= n
            if role == 'innocent'
            else z3.Sum([z3.If(c, 1, 0) for c in cells]) < len(cells) - n
        )

    # return rule that assigns role to role_zone, and !role to zone - zone-role
    def split_roles_in_zone(self, zone, zone_role, role):
        print("!! AND !!")
        return z3.And(
            self.predicat(zone_role, len(zone_role), role),
            self.predicat(zone, len(zone_role), role),
        )

    def or_range_predicat(self, cell_indices: list[tuple], range: range, role='innocent'):
        print("!! OR !!")
        return z3.Or([self.predicat(cell_indices, i, role) for i in range])

    def parity_in_zone(self, cell_indices: list[tuple], parity: str, role='innocent'):
        start = 0 if parity == 'even' else 1
        return self.or_range_predicat(cell_indices, range(start, len(cell_indices), 2), role)

    def pos_to_cells(self, pos: Tree) -> list[Cell]:
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
                dir_tree = pos.children[0]
                name = pos.children[1].value
                side = (
                    dir_tree.children[0].value if dir_tree.data == "to_side_of" else dir_tree.data
                )
                return Cell.dir[side](self.people[name].id)

    @staticmethod
    def replace_me_values(node: Tree, name: str) -> None:
        if isinstance(node, Token):
            return Token(node.type, name) if node.value in ["me", "I"] else node
        for i, child in enumerate(node.children):
            node.children[i] = Clue.replace_me_values(child, name)
        return node


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
