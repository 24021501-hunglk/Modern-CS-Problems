from time import perf_counter

from pysat.formula import IDPool
from pysat.solvers import Solver

from threading import Timer

TIMEOUT_SECONDS = 180

class NQueensCommander:
    def __init__(self, n, group_size=3):
        self.n = n
        self.group_size = group_size
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

    def at_most_one_commander(self, variables):
        if len(variables) <= 1:
            return

        if len(variables) <= self.group_size:
            self.add_pairwise_amo(variables)
            return

        groups = [
            variables[i:i + self.group_size]
            for i in range(0, len(variables), self.group_size)
        ]

        commanders = []

        for group in groups:
            commander = self.vpool.id()
            commanders.append(commander)

            self.add_pairwise_amo(group)

            for variable in group:
                self.clauses.append([-variable, commander])

        self.at_most_one_commander(commanders)

    def build(self):
        n = self.n

        for row in range(n):
            variables = [
                self.var(row, col)
                for col in range(n)
            ]

            self.clauses.append(variables)

            self.at_most_one_commander(variables)

        for col in range(n):
            variables = [
                self.var(row, col)
                for row in range(n)
            ]
            self.at_most_one_commander(variables)

        for d in range(-(n - 1), n):
            variables = []

            for row in range(n):
                col = row - d
                if 0 <= col < n:
                    variables.append(self.var(row, col))

            self.at_most_one_commander(variables)

        for s in range(2 * n - 1):
            variables = []

            for row in range(n):
                col = s - row
                if 0 <= col < n:
                    variables.append(self.var(row, col))

            self.at_most_one_commander(variables)

        return self.clauses

    def solve(self):
        start_encoding = perf_counter()
        clauses = self.build()
        end_encoding = perf_counter()

        with Solver(name="glucose3") as solver:
            start_loading = perf_counter()
            for clause in clauses:
                solver.add_clause(clause)
            end_loading = perf_counter()

            start_solving = perf_counter()

            timer = Timer(
                TIMEOUT_SECONDS,
                solver.interrupt
            )
            timer.start()

            try:
                satisfiable = solver.solve_limited(expect_interrupt=True)
            finally:
                timer.cancel()
                solver.clear_interrupt()

            end_solving = perf_counter()
            
            if satisfiable is None:
                print("Status: TIMEOUT")
                print(f"Encoding time: {encoding_time:.6f} seconds")
                print(f"Loading time: {loading_time:.6f} seconds")
                print(f"Solving time: {end_solving - start_solving:.6f} seconds")
                print(
                    f"Total time: "
                    f"{encoding_time + loading_time + (end_solving - start_solving):.6f} seconds"
                )
                return None
            
            print(f"Status: {'SAT' if satisfiable else 'UNSAT'}")
            
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
        auxiliary_vars = total_vars - primary_vars

        encoding_time = end_encoding - start_encoding
        loading_time = end_loading - start_loading
        solving_time = end_solving - start_solving
        total_time = encoding_time + loading_time + solving_time

        print(f"N: {self.n}")
        print(f"Group size: {self.group_size}")
        print(f"Primary variables: {primary_vars}")
        print(f"Auxiliary variables: {auxiliary_vars}")
        print(f"Total variables: {total_vars}")
        print(f"Clauses: {len(clauses)}")
        print(f"Encoding time: {encoding_time:.6f} seconds")
        print(f"Loading time: {loading_time:.6f} seconds")
        print(f"Solving time: {solving_time:.6f} seconds")
        print(f"Total time: {total_time:.6f} seconds")

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
    n = 10

    problem = NQueensCommander(n, group_size=8)
    board = problem.solve()

    if board is not None:
        print("\nSolution:")
        problem.print_board(board)

        print("\nQueen positions (row, column):")
        for row, col in enumerate(board):
            print(f"({row}, {col})")
