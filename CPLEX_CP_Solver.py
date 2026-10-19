import os
import sys
import time

from docplex.cp.model import CpoModel
from docplex.cp.config import context


CPLEX_STUDIO_DIR = (
    r"C:\Program Files\IBM\ILOG\CPLEX_Studio_Community222"
)

CPLEX_CP_DIR = os.path.join(
    CPLEX_STUDIO_DIR,
    "cpoptimizer",
    "bin",
    "x64_win64"
)

CPLEX_CP_EXE = os.path.join(CPLEX_CP_DIR, "cpoptimizer.exe")


def configure_cplex():
    if not os.path.isfile(CPLEX_CP_EXE):
        raise FileNotFoundError(
            "Cannot find cpoptimizer.exe at:\n"
            f"{CPLEX_CP_EXE}\n"
            "Please check CPLEX_STUDIO_DIR."
        )

    os.environ["PATH"] = (
        CPLEX_CP_DIR + os.pathsep + os.environ.get("PATH", "")
    )

    context.solver.local.execfile = CPLEX_CP_EXE


def solve_n_queens(n):
    if n < 1:
        raise ValueError("N must be a positive integer.")

    mdl = CpoModel(name="N_Queens_CPLEX_CP")

    x = [
        mdl.integer_var(min=0, max=n - 1, name=f"x_{i}")
        for i in range(n)
    ]

    mdl.add(mdl.all_diff(x))

    mdl.add(mdl.all_diff([x[i] + i for i in range(n)]))
    mdl.add(mdl.all_diff([x[i] - i for i in range(n)]))

    start_time = time.perf_counter()

    solution = mdl.solve(TimeLimit=60)

    solve_time = time.perf_counter() - start_time

    status = solution.get_solve_status()
    print(f"\nN = {n}")
    print("Status:", status)
    print(f"Solve time: {solve_time:.6f} seconds")

    if status not in ("Feasible", "Optimal"):
        print("No solution was found within the time limit.")
        return

    positions = [solution.get_value(x[i]) for i in range(n)]

    print("\nBoard:")
    for row in range(n):
        line = ["."] * n
        line[positions[row]] = "Q"
        print(" ".join(line))

    print("\nQueen positions (row, column), 1-based:")
    for row, col in enumerate(positions):
        print(f"({row + 1}, {col + 1})")


if __name__ == "__main__":
    try:
        configure_cplex()
        n = 80
        solve_n_queens(n)

    except ValueError as error:
        print("Invalid input:", error)
        print("Usage: python CPLEX_CP_Solver.py <N>")

    except Exception as error:
        print("Error while running CPLEX CP:")
        print(error)
