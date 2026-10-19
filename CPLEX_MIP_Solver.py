import sys
import time
from docplex.mp.model import Model


def solve_n_queens(n):
    if n < 1:
        raise ValueError("N must be a positive integer.")

    mdl = Model(name="N_Queens_CPLEX_MIP")

    x = {
        (i, j): mdl.binary_var(name=f"x_{i}_{j}")
        for i in range(n)
        for j in range(n)
    }

    for i in range(n):
        mdl.add_constraint(
            mdl.sum(x[i, j] for j in range(n)) == 1,
            ctname=f"row_{i}"
        )

    for j in range(n):
        mdl.add_constraint(
            mdl.sum(x[i, j] for i in range(n)) == 1,
            ctname=f"col_{j}"
        )

    for d in range(-(n - 1), n):
        mdl.add_constraint(
            mdl.sum(
                x[i, j]
                for i in range(n)
                for j in range(n)
                if i - j == d
            ) <= 1,
            ctname=f"diag_main_{d}"
        )

    for s in range(2 * n - 1):
        mdl.add_constraint(
            mdl.sum(
                x[i, j]
                for i in range(n)
                for j in range(n)
                if i + j == s
            ) <= 1,
            ctname=f"diag_anti_{s}"
        )

    mdl.set_time_limit(60)

    start_time = time.perf_counter()
    solution = mdl.solve(log_output=False)
    solve_time = time.perf_counter() - start_time

    print(f"\nN = {n}")
    print("Status:", mdl.solve_details.status)
    print(f"Solve time: {solve_time:.6f} seconds")

    if solution is None:
        print("No solution found within the time limit.")
        mdl.end()
        return
    
    board = []
    for i in range(n):
        row = []
        for j in range(n):
            row.append("Q" if solution.get_value(x[i, j]) > 0.5 else ".")
        board.append(row)

    print("\nBoard:")
    for row in board:
        print(" ".join(row))

    print("\nQueen positions (row, column), 1-based:")
    for i in range(n):
        for j in range(n):
            if solution.get_value(x[i, j]) > 0.5:
                print(f"({i + 1}, {j + 1})")

    mdl.end()


if __name__ == "__main__":
    try:
        n = 31
        solve_n_queens(n)
    except ValueError as error:
        print("Invalid input:", error)
        print("Usage: python CPLEX_MIP_Solver.py <N>")
    except Exception as error:
        print("Error while running CPLEX MIP:")
        print(error)
