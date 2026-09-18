import z3
from lark import Tree, Token
from itertools import combinations

from game_elements import Cell, Row, Column
from interpreter import (
    predicat,
    predicat_neq,
    predicat_less,
    predicat_as_many,
    predicat_more_eq,
    predicat_more_zone,
    predicat_nb_more_zone,
    parity_in_zone,
    split_roles_in_zone,
)


class Clue:
    types = {}

    def __init_subclass__(cls):
        Clue.types[cls.__name__] = cls

    def __init__(self, tree: Tree, name: str):
        var_names = []
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
        var_stem = "name" if var_stem == "my" else var_stem

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
            return Row if element.value in ["row", "rows"] else Column
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
    def replace_me_values(node: Tree | Token, name: str) -> Tree | Token:  # TODO: change this
        """Iterate through tree to replace 'me, 'my', 'I' values"""
        if isinstance(node, Token):
            print(node.type)
            return Token(node.type, name) if node.value in ["me", "I", "my"] else node
            # return Token("NAME", name) if node.value in ["me", "I", "my"] else node
        for i, child in enumerate(node.children):
            node.children[i] = Clue.replace_me_values(child, name)
        return node


class T_1(Clue):
    def get_rule(self):
        cells = Cell.pos_to_cells(self.pos)
        cells2 = Cell.pos_to_cells(self.pos2)
        inter = Cell.intersection(cells, cells2)
        return z3.And(
            predicat(inter, self.nb, self.role),
            predicat(cells, self.nb2, self.role),
        )


class T_2(Clue):
    def get_rule(self):
        cells = Cell.pos_to_cells(self.pos)
        cells2 = Cell.pos_to_cells(self.pos2)
        inter = Cell.intersection(cells, cells2)

        return predicat(inter, self.nb, self.role)


class T_3(Clue):
    def get_rule(self):
        cells = Cell.neighbors(self.name)
        cells2 = Cell.neighbors(self.name2)
        inter = Cell.intersection(cells, cells2)

        return z3.And(
            predicat(inter, self.nb, self.role),
            predicat(cells, self.nb2, self.role),
        )


class T_4(Clue):
    def get_rule(self):
        cells = Cell.neighbors(self.name)
        cells2 = Cell.pos_to_cells(self.pos)
        inter = Cell.intersection(cells, cells2)

        return (predicat(inter, self.nb, self.role),)


class T_5(Clue):
    def get_rule(self):
        cells = Cell.job_to_cells(self.job)
        cells2 = Cell.pos_to_cells(self.pos)
        inter = Cell.intersection(cells, cells2)
        return z3.And(
            predicat(inter, self.nb, self.role),
            predicat(cells, self.nb2, self.role),
        )


class T_6(Clue):
    def get_rule(self):
        cells = Cell.job_to_cells(self.job)
        cells2 = Cell.pos_to_cells(self.pos)
        inter = Cell.intersection(cells, cells2)

        return predicat(inter, self.nb, self.role)


class T_7(Clue):
    def get_rule(self):
        cells = Cell.pos_to_cells(self.pos)
        name_cell = Cell.name_to_cell(self.name)
        return z3.And(
            predicat(cells, self.nb, self.role),
            predicat([name_cell], 1, self.role),
        )


class T_8(Clue):
    def get_rule(self):
        cells = Cell.neighbors(self.name2)
        name_cell = Cell.name_to_cell(self.name)
        return z3.And(
            predicat(cells, self.nb, self.role),
            predicat([name_cell], 1, self.role),
        )


class T_9(Clue):
    def get_rule(self):
        cells = Cell.neighbors(self.name)
        return predicat(cells, self.nb, self.role)


class T_10(Clue):
    def get_rule(self):
        cells = Cell.neighbors(self.pos)
        name_cell = Cell.name_to_cell(self.name)
        neighbors = Cell.neighbors_from_coords(name_cell)
        return z3.And(
            [predicat(neighbors, self.nb, self.role)]
            + [
                predicat_neq(Cell.neighbors_from_coords(c), self.nb, self.role)
                for c in cells
                if c != name_cell
            ]
        )


class T_11(Clue):
    def get_rule(self):
        cell = Cell.name_to_cell(self.name)
        return predicat([cell], 1, self.role)


class T_12(Clue):
    def get_rule(self):
        neighbors = Cell.neighbors(self.name)
        cells = Cell.pos_to_cells(self.pos)
        inter = Cell.intersection(cells, neighbors)
        return predicat(inter, self.nb, self.role)


class T_13(Clue):
    def get_rule(self):
        cells = Cell.pos_to_cells(self.pos)
        return predicat(cells, self.nb, self.role)


class T_14(Clue):
    def get_rule(self):
        cells = Cell.pos_to_cells(self.pos)
        return predicat_more_eq(cells, self.nb, self.role)


class T_15(Clue):
    def get_rule(self):
        cells = self.axis.cells(self.coord)
        cells2 = self.axis.cells(self.coord2)
        return predicat_more_zone(cells, cells2, self.role)


class T_16(Clue):
    def get_rule(self):
        cells = self.axis.cells(self.coord)
        cells2 = self.axis.cells(self.coord2)
        return predicat_more_zone(cells2, cells, self.role)


class T_17(Clue):
    def get_rule(self):
        cells = self.axis.cells(self.coord)
        cells2 = self.axis.cells(self.coord2)
        return predicat_as_many(cells, cells2, self.role, self.role)


class T_18(Clue):
    def get_rule(self):
        cells = Cell.job_to_cells(self.job)
        return predicat(cells, self.nb, self.role)


class T_19(Clue):
    def get_rule(self):
        cells = Cell.job_to_cells(self.job)
        return predicat_more_eq(cells, self.nb, self.role)


class T_20(Clue):
    def get_rule(self):
        return z3.And(
            [
                predicat_more_eq(self.axis.cells(ax_coord), self.nb, self.role)
                for ax_coord in self.axis.range()
            ]
        )


class T_21(Clue):
    def get_rule(self):
        return z3.Or(
            [
                z3.And(
                    [predicat(self.axis.cells(ax_coord), self.nb, self.role)]
                    + [
                        predicat_neq(self.axis.cells(others), self.nb, self.role)
                        for others in self.axis.range()
                        if others != ax_coord
                    ]
                )
                for ax_coord in self.axis.range()
            ]
        )


class T_22(Clue):
    def get_rule(self):
        return z3.And(
            [predicat(self.axis.cells(self.coord), self.nb, self.role)]
            + [
                predicat_neq(self.axis.cells(ax_coord), self.nb, self.role)
                for ax_coord in self.axis.range()
                if ax_coord != self.coord
            ]
        )


class T_23(Clue):
    def get_rule(self):
        cells = self.axis.cells(self.axis_coord)
        return z3.And(
            [
                predicat_more_zone(self.axis.cells(self.coord), self.axis.cells(other), self.role)
                for other in self.axis.range()
                if other != self.axis_coord
            ]
        )


class T_24(Clue):
    def get_rule(self):
        cells = self.axis.cells(self.axis_coord)
        return z3.And(
            [
                predicat_more_zone(self.axis.cells(other), self.axis.cells(self.coord), self.role)
                for other in self.axis.range()
                if other != self.axis_coord
            ]
        )


class T_25(Clue):  # TODO: Fix
    def get_rule(self):
        cells = Cell.job_to_cells(self.job)
        cells2 = Cell.job_to_cells(self.job2)
        return predicat_less(cells2, cells, self.role2, self.role)


class T_26(Clue):  # TODO: Fix
    def get_rule(self):
        cells = Cell.job_to_cells(self.job)
        cells2 = Cell.job_to_cells(self.job2)
        return predicat_less(cells, cells2, self.role, self.role2)


class T_27(Clue):
    def get_rule(self):
        cells = Cell.job_to_cells(self.job)
        cells2 = Cell.job_to_cells(self.job2)
        return predicat_as_many(cells, cells2, self.role, self.role2)


class T_28(Clue):
    def get_rule(self):
        cells = Cell.pos_to_cells(self.pos)
        return z3.And([predicat(Cell.neighbors(c), 0, self.role) for c in cells])


class T_29(Clue):
    def get_rule(self):
        cells = Cell.neighbors(self.name)
        cells2 = Cell.neighbors(self.name2)
        return predicat_nb_more_zone(cells2, cells, self.role, self.nb)


class T_30(Clue):
    def get_rule(self):
        cells = Cell.neighbors(self.name)
        cells2 = Cell.neighbors(self.name2)
        return predicat_nb_more_zone(cells, cells2, self.role, self.nb)


class T_31(Clue):
    def get_rule(self):
        cells = Cell.neighbors(self.name)
        cells2 = Cell.pos_to_cells(self.pos)
        inter = Cell.intersection(cells, cells2)
        return parity_in_zone(inter, self.parity, self.role)


class T_32(Clue):
    def get_rule(self):
        cells = Cell.neighbors(self.name)
        cells2 = Cell.pos_to_cells(self.pos)
        inter = Cell.intersection(cells, cells2)
        return parity_in_zone(inter, self.parity, self.role)


class T_33(Clue):
    def get_rule(self):
        cells = Cell.pos_to_cells(self.pos)
        return parity_in_zone(cells, self.parity, self.role)


class T_34(Clue):
    def get_rule(self):
        pos_cells = Cell.pos_to_cells(self.pos)
        if self.allboth == "both":
            cells_groups = Cell.n_connected(pos_cells, 2)
        else:
            cells_groups = Cell.any_connected(pos_cells)

        return z3.Or([split_roles_in_zone(pos_cells, group, self.role) for group in cells_groups])


class T_35(Clue):
    def get_rule(self):
        cells = Cell.neighbors(self.name)
        cells2 = Cell.neighbors(self.name2)
        inter = Cell.intersection(cells, cells2)
        return predicat(inter, self.nb, self.role)


class T_36(Clue):
    def get_rule(self):
        cells = Cell.pos_to_cells(self.pos)
        zone_dir = list(Cell.zone_directly_dir(cells, self.dir).values())
        return predicat(zone_dir, self.nb, self.role)


class T_37(Clue):
    def get_rule(self):
        cells = Cell.job_to_cells(self.job)
        zone_dir = list(Cell.zone_directly_dir(cells, self.dir).values())
        return predicat(zone_dir, self.nb, self.role)


class T_38(Clue):
    def get_rule(self):
        cells = Cell.job_to_cells(self.job)
        return predicat(cells, len(cells), self.role)


class T_39(Clue):
    def get_rule(self):
        cells = Cell.neighbors(self.name)
        return predicat_more_eq(cells, self.nb, self.role)


class T_40(Clue):  # TODO: fix
    def get_rule(self):
        cells = Cell.neighbors(self.name)
        cells2 = Cell.neighbors(self.name2)
        return predicat_as_many(cells, cells2, self.role)


class T_41(Clue):
    def get_rule(self):
        cells = Cell.pos_to_cells(self.pos)
        zone_dir = list(Cell.zone_directly_dir(cells, self.dir).values())
        return predicat(zone_dir, self.nb, self.role)


class T_42(Clue):
    def get_rule(self):
        cells = Cell.pos_to_cells(self.pos)
        # zone_dir = list(Cell.zone_directly_dir(cells, self.dir).values())
        zone_dir = Cell.zone_directly_dir(cells, self.dir)
        combs = list(combinations(list(zone_dir.items()), self.nb))

        return z3.Or(
            [
                z3.And(
                    [
                        z3.And(
                            predicat([pair[0]], 1, self.role),
                            predicat([pair[1]], 1, self.role2),
                        )
                        for pair in comb
                    ]
                    + [
                        z3.Or(
                            predicat_neq([pair[0]], 1, self.role),
                            predicat_neq([pair[1]], 1, self.role2),
                        )
                        for pair in list(zone_dir.items())
                        if pair not in comb
                    ]
                )
                for comb in combs
            ]
        )


class T_43(Clue):
    def get_rule(self):
        name_cell = Cell.name_to_cell(self.name)
        cells = Cell.neighbors(self.name)
        return z3.And(
            [predicat(cells, self.nb, self.role)]
            + [
                predicat_neq(Cell.neighbors_from_coords(c), self.nb, self.role)
                for c in Cell.all_cells()
                if c != name_cell
            ]
        )


class T_44(Clue):
    def get_rule(self):
        cells = Cell.pos_to_cells(self.pos)
        return z3.And(
            [predicat_less(Cell.neighbors_from_coords(c), self.nb + 1, self.role) for c in cells]
        )


class T_45(Clue):
    def get_rule(self):
        cells = Cell.pos_to_cells(self.pos)
        return z3.And(
            [predicat_more_eq(Cell.neighbors_from_coords(c), self.nb, self.role) for c in cells]
        )


class T_46(Clue):
    def get_rule(self):
        cells = Cell.pos_to_cells(self.pos)
        neighbors = [Cell.neighbors_from_coords(c) for c in cells]
        combs = list(combinations(neighbors, self.nb))
        return z3.Or(
            [
                z3.And(
                    [predicat(n, self.nb2, self.role) for n in neighbors if n in comb]
                    + [predicat_neq(n, self.nb2, self.role) for n in neighbors if n not in comb]
                )
                for comb in combs
            ]
        )
