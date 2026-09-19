Python program to solve today's [Clues by Sam](cluesbysam.com) puzzle.

### Install
Download this project:
```
git clone https://github.com/ClementCourcelle/cluesbysam_solver.git
```

If needed, create a python virtual environment and activate it:
```
python3 -m venv /path/to/venv
source /path/to/venv/bin/activate
```

Install the project dependencies and a playwright browser:
```
cd cluesbysam_solver
pip install .
playwright install
playwright install-deps
```

### Usage

Activate your virtual environment if needed. Then:
```
cd cluesbysam_solver
python3 src/main.py
```

If you use it multiple times, you can use `-i` option to interrupt the program before completing the last step to not mess with the website statistics.

### Note
The program to update the clues grammar do not work anymore.
