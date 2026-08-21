from pathlib import Path
from lark import Lark

GRAMMAR_DIR = Path(__file__).parent.parent.parent / "grammar"

base = (GRAMMAR_DIR / "grammar_base.lark").read_text()
base += (GRAMMAR_DIR / "clue_types.lark").read_text()

names = ["alice", "bob"]
names = " | ".join(f'"{n}"' for n in names) + ' | "me" | "i"'
jobs = ["pilot", "cop"]
jobs = " | ".join(f'"{n}"' for n in jobs)

grammar = "\n".join(
    [
        base,
        # f"NAME_S: {names_s}",
        f"NAME: {names}",
        f"JOB: {jobs}",
    ]
)

print(grammar)
print("\n========== TESTS ==========\n")

parser = Lark(grammar, parser="earley", ambiguity="resolve", propagate_positions=True)
tree = parser.parse(("each column has at least 3 innocents").lower())
print(tree.pretty())
print("\n Full :\n")
print(tree)
print("\n=== POS ===\n")
print(tree.children[0].children[3].data)
print(tree.children[0].children[2].type)
print(tree.children[0].children[2].value)
print(tree.children[0].children[3].children[0])
print(tree.children[0].children[4].children[0].children[0].value)
