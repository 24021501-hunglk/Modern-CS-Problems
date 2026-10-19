from time import perf_counter

from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.solvers import Solver


class NQueensBinary:
    def __init__(self, n):
        self.n = n
        self.clauses = []
        self.vpool = IDPool(start_from=n * n + 1)

    def var(self, row, col):
        return row * self.n + col + 1

    def at_most_one_binary(self, variables):
        if len(variables) <= 1:
            return

        encoding = CardEnc.atmost(
            lits=variables,
            bound=1,
            encoding=EncType.bitwise,
            vpool=self.vpool
        )

        self.clauses.extend(encoding.clauses)

    def build(self):
        n = self.n

        for row in range(n):
            variables = [
                self.var(row, col) for col in range(n)
            ]
            self.clauses.append(variables)
            self.at_most_one_binary(variables)

        for col in range(n):
            variables = [
                self.var(row, col) for row in range(n)
            ]
            self.at_most_one_binary(variables)

        for d in range(-(n - 1), n):
            variables = [
                self.var(row, row - d)
                for row in range(n)
                if 0 <= row - d < n
            ]
            self.at_most_one_binary(variables)

        for s in range(2 * n - 1):
            variables = [
                self.var(row, s - row)
                for row in range(n)
                if 0 <= s - row < n
            ]
            self.at_most_one_binary(variables)

        return self.clauses

    def solve(self):
        clauses = self.build()
        start = perf_counter()

        with Solver(name="glucose3") as solver:
            for clause in clauses:
                solver.add_clause(clause)

            if not solver.solve():
                print("No solution found.")
                return None

            model = {
                lit for lit in solver.get_model()
                if lit > 0
            }

        elapsed = perf_counter() - start

        board = []
        for row in range(self.n):
            queen_col = next(
                col for col in range(self.n)
                if self.var(row, col) in model
            )
            board.append(queen_col)

        print(f"N: {self.n}")
        print(f"Primary variables: {self.n * self.n}")
        print(f"Total variables: {self.vpool.top}")
        print(f"Auxiliary variables: {self.vpool.top - self.n * self.n}")
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

    problem = NQueensBinary(n)
    board = problem.solve()

    if board is not None:
        print("\nSolution:")
        problem.print_board(board)