import sys
import time

from ortools.sat.python import cp_model

def solve_n_queens(n):
    if n < 1:
        raise ValueError("N must be a positive integer.")

    model = cp_model.CpModel()

    x = [
        [
            model.new_bool_var(f"x_{i}_{j}")
            for j in range(n)
        ]
        for i in range(n)
    ]

    for i in range(n):
        model.add_exactly_one(x[i])

    for j in range(n):
        model.add_exactly_one(x[i][j] for i in range(n))

    for d in range(-(n - 1), n):
        diagonal = [
            x[i][j]
            for i in range(n)
            for j in range(n)
            if i - j == d
        ]
        if len(diagonal) > 1:
            model.add_at_most_one(diagonal)

    for s in range(2 * n - 1):
        diagonal = [
            x[i][j]
            for i in range(n)
            for j in range(n)
            if i + j == s
        ]
        if len(diagonal) > 1:
            model.add_at_most_one(diagonal)

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 60.0

    start_time = time.perf_counter()
    status = solver.solve(model)
    solve_time = time.perf_counter() - start_time

    print(f"\nN = {n}")
    print("Status:", solver.status_name(status))
    print(f"Solve time: {solve_time:.6f} seconds")

    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        print("No solution found within the time limit.")
        return

    positions = []
    print("\nBoard:")

    for i in range(n):
        queen_col = next(
            j for j in range(n)
            if solver.value(x[i][j]) == 1
        )
        positions.append(queen_col)

        row = ["."] * n
        row[queen_col] = "Q"
        print(" ".join(row))

    print("\nQueen positions (row, column), 1-based:")
    for i, j in enumerate(positions):
        print(f"({i + 1}, {j + 1})")


if __name__ == "__main__":
    try:
        n = 80
        solve_n_queens(n)
    except ValueError as error:
        print("Invalid input:", error)
        print("Usage: python CP_SAT_Solver.py <N>")
    except Exception as error:
        print("Error while running CP-SAT:")
        print(error)
