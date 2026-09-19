import z3
from game_elements import Status


class Constraint:
    grid = None

    @staticmethod
    def predicat(cell_indices: list[tuple], n: int, role=Status.INNOCENT):
        """Return rule to assign number of roles to a zone"""
        cells = [Constraint.grid[c[0], c[1]] for c in cell_indices]
        return (
            z3.Sum([z3.If(c, 1, 0) for c in cells]) == n
            if role == Status.INNOCENT
            else Constraint.predicat(cell_indices, len(cells) - n)
        )

    @staticmethod
    def predicat_neq(cell_indices: list[tuple], n: int, role=Status.INNOCENT):
        """Return rule to forbid number of roles to a zone"""
        print(f"NON EQUAL")
        print(f"{cell_indices = }")
        print(f"{n = }")
        print(f"{role = }")
        cells = [Constraint.grid[c[0], c[1]] for c in cell_indices]
        return (
            z3.Sum([z3.If(c, 1, 0) for c in cells]) != n
            if role == Status.INNOCENT
            else Constraint.predicat_neq(cell_indices, len(cells) - n)
        )

    @staticmethod
    def predicat_less(cell_indices: list[tuple], n: int, role=Status.INNOCENT):
        """Return rule to assign maximum number of roles to a zone"""
        print(f"MORE")
        print(f"{cell_indices = }")
        print(f"{n = }")
        print(f"{role = }")
        cells = [Constraint.grid[c[0], c[1]] for c in cell_indices]
        return (
            z3.Sum([z3.If(c, 1, 0) for c in cells]) < n
            if role == Status.INNOCENT
            else z3.Sum([z3.If(c, 1, 0) for c in cells]) > len(cells) - n
        )

    @staticmethod
    def predicat_more_eq(cell_indices: list[tuple], n: int, role=Status.INNOCENT):
        """Return rule to assign minimum number of roles to a zone"""
        print(f"MORE")
        print(f"{cell_indices = }")
        print(f"{n = }")
        print(f"{role = }")
        cells = [Constraint.grid[c[0], c[1]] for c in cell_indices]
        return (
            z3.Sum([z3.If(c, 1, 0) for c in cells]) >= n
            if role == Status.INNOCENT
            else z3.Sum([z3.If(c, 1, 0) for c in cells]) <= len(cells) - n
        )

    @staticmethod
    def predicat_more_zone(cell_indices: list[tuple], cell_indices2: list[tuple], role: Status):
        """Return rule to assign more roles in cells than cells2"""
        print(f"MORE")
        cells = [Constraint.grid[c[0], c[1]] for c in cell_indices]
        cells2 = [Constraint.grid[c[0], c[1]] for c in cell_indices2]
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

    @staticmethod
    def predicat_as_many(
        cell_indices: list[tuple], cell_indices2: list[tuple], role: Status, role2: Status
    ):
        """Return rule to assign as many roles in two zones"""
        print(f"AS MANY")
        cells = [Constraint.grid[c[0], c[1]] for c in cell_indices]
        cells2 = [Constraint.grid[c[0], c[1]] for c in cell_indices2]
        sum = (
            z3.Sum([z3.If(c, 1, 0) for c in cells])
            if role == Status.INNOCENT
            else z3.Sum([z3.If(c, 0, 1) for c in cells])
        )
        sum2 = (
            z3.Sum([z3.If(c, 1, 0) for c in cells2])
            if role2 == Status.INNOCENT
            else z3.Sum([z3.If(c, 0, 1) for c in cells2])
        )
        return sum == sum2

    @staticmethod
    def predicat_nb_more_zone(
        cell_indices: list[tuple], cell_indices2: list[tuple], role: Status, nb: int
    ):
        """Return rule to assign nb more roles in cells than cells2"""
        print(f"MORE")
        cells = [Constraint.grid[c[0], c[1]] for c in cell_indices]
        cells2 = [Constraint.grid[c[0], c[1]] for c in cell_indices2]
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
        return sum == sum2 + nb

    @staticmethod
    def split_roles_in_zone(zone, zone_role, role):
        """Return rule that assigns all the roles cells to to one part of a zone"""  # pire commentaire
        print(f"{zone = }")
        print(f"{zone_role = }")
        print("!! AND !!")
        return z3.And(
            Constraint.predicat(zone_role, len(zone_role), role),
            Constraint.predicat(zone, len(zone_role), role),
        )

    @staticmethod
    def or_range_predicat(cell_indices: list[tuple], range: range, role=Status.INNOCENT):
        """Return OR rules with range of possible number of roles"""  # 2e pire commentaire
        print("!! OR !!")
        return z3.Or([Constraint.predicat(cell_indices, i, role) for i in range])

    @staticmethod
    def parity_in_zone(cell_indices: list[tuple], parity: str, role=Status.INNOCENT):
        """Return rules with possible role values based on parity"""  # 3e pire commentaire
        start = 0 if parity == 'even' else 1
        return Constraint.or_range_predicat(cell_indices, range(start, len(cell_indices), 2), role)
