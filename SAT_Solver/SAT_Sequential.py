from time import perf_counter

from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.solvers import Solver

class NQueensSequential:
    def __init__(self, n):
        self.n = n
        self.clauses = []

        self.vpool = IDPool(start_from=n * n + 1)

    def var(self, row, col):
        return row * self.n + col + 1

    def at_most_one_sequential(self, variables):
        if len(variables) <= 1:
            return

        encoding = CardEnc.atmost(
            lits=variables,
            bound=1,
            encoding=EncType.seqcounter,
            vpool=self.vpool
        )

        self.clauses.extend(encoding.clauses)

    def build(self):
        n = self.n

        for row in range(n):
            variables = [
                self.var(row, col)
                for col in range(n)
            ]

            self.clauses.append(variables)

            self.at_most_one_sequential(variables)

        for col in range(n):
            variables = [
                self.var(row, col)
                for row in range(n)
            ]
            self.at_most_one_sequential(variables)

        for d in range(-(n - 1), n):
            variables = []

            for row in range(n):
                col = row - d

                if 0 <= col < n:
                    variables.append(self.var(row, col))

            self.at_most_one_sequential(variables)

        for s in range(2 * n - 1):
            variables = []

            for row in range(n):
                col = s - row

                if 0 <= col < n:
                    variables.append(self.var(row, col))

            self.at_most_one_sequential(variables)

        return self.clauses

    def solve(self):
        clauses = self.build()

        start = perf_counter()

        with Solver(name="glucose3") as solver:
            for clause in clauses:
                solver.add_clause(clause)

            elapsed = perf_counter() - start

            if not solver.solve():
                print("No solution found.")
                return None

            model = set(lit for lit in solver.get_model() if lit > 0)

        board = []

        for row in range(self.n):
            queen_col = None

            for col in range(self.n):
                if self.var(row, col) in model:
                    queen_col = col
                    break

            board.append(queen_col)

        primary_vars = self.n * self.n
        total_vars = self.vpool.top

        print(f"N: {self.n}")
        print(f"Primary variables: {primary_vars}")
        print(f"Auxiliary variables: {total_vars - primary_vars}")
        print(f"Total variables: {total_vars}")
        print(f"Clauses: {len(clauses)}")
        print(f"Solve time: {elapsed:.6f} seconds")

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

    problem = NQueensSequential(n)
    board = problem.solve()

    if board is not None:
        print("\nSolution:")
        problem.print_board(board)

        print("\nQueen positions (row, column):")
        for row, col in enumerate(board):
            print(f"({row}, {col})")
