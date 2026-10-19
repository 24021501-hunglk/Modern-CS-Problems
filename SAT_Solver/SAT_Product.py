from math import ceil, sqrt
from time import perf_counter

from pysat.formula import IDPool
from pysat.solvers import Solver


class NQueensProduct:
    def __init__(self, n):
        self.n = n
        self.clauses = []
        self.vpool = IDPool(start_from=n * n + 1)

    def var(self, row, col):
        return row * self.n + col + 1

    def add_pairwise_amo(self, variables):
        for i in range(len(variables)):
            for j in range(i + 1, len(variables)):
                self.clauses.append([
                    -variables[i],
                    -variables[j]
                ])

    def at_most_one_product(self, variables):
        m = len(variables)

        if m <= 1:
            return

        rows = ceil(sqrt(m))
        cols = ceil(m / rows)

        row_selectors = [
            self.vpool.id() for _ in range(rows)
        ]
        col_selectors = [
            self.vpool.id() for _ in range(cols)
        ]

        for k, variable in enumerate(variables):
            i = k // cols
            j = k % cols

            self.clauses.append([
                -variable,
                row_selectors[i]
            ])

            self.clauses.append([
                -variable,
                col_selectors[j]
            ])

        self.add_pairwise_amo(row_selectors)
        self.add_pairwise_amo(col_selectors)

    def build(self):
        n = self.n

        for row in range(n):
            variables = [
                self.var(row, col)
                for col in range(n)
            ]

            self.clauses.append(variables)

            self.at_most_one_product(variables)

        for col in range(n):
            variables = [
                self.var(row, col)
                for row in range(n)
            ]
            self.at_most_one_product(variables)

        for d in range(-(n - 1), n):
            variables = []

            for row in range(n):
                col = row - d

                if 0 <= col < n:
                    variables.append(self.var(row, col))

            self.at_most_one_product(variables)

        for s in range(2 * n - 1):
            variables = []

            for row in range(n):
                col = s - row

                if 0 <= col < n:
                    variables.append(self.var(row, col))

            self.at_most_one_product(variables)

        return self.clauses

    def solve(self):
        start_encoding = perf_counter()
        clauses = self.build()
        end_encoding = perf_counter()

        start_solver = perf_counter()

        with Solver(name="glucose3") as solver:
            for clause in clauses:
                solver.add_clause(clause)

            end_loading = perf_counter()
            satisfiable = solver.solve()
            end_solving = perf_counter()

            if not satisfiable:
                print("No solution found.")
                return None

            model = {
                lit for lit in solver.get_model()
                if lit > 0
            }

        board = []

        for row in range(self.n):
            queen_col = next(
                col for col in range(self.n)
                if self.var(row, col) in model
            )
            board.append(queen_col)

        primary_vars = self.n * self.n
        total_vars = self.vpool.top

        print(f"N: {self.n}")
        print(f"Primary variables: {primary_vars}")
        print(f"Auxiliary variables: {total_vars - primary_vars}")
        print(f"Total variables: {total_vars}")
        print(f"Clauses: {len(clauses)}")
        print(
            f"Encoding time: "
            f"{end_encoding - start_encoding:.6f} seconds"
        )
        print(
            f"Loading time: "
            f"{end_loading - start_solver:.6f} seconds"
        )
        print(
            f"Solving time: "
            f"{end_solving - end_loading:.6f} seconds"
        )

        return board

    def print_board(self, board):
        if board is None:
            return

        for row in range(self.n):
            print(" ".join(
                "Q" if board[row] == col else "."
                for col in range(self.n)
            ))


if __name__ == "__main__":
    n = 80

    problem = NQueensProduct(n)
    board = problem.solve()

    if board is not None:
        print("\nSolution:")
        problem.print_board(board)

        print("\nQueen positions (row, column):")
        for row, col in enumerate(board):
            print(f"({row}, {col})")
