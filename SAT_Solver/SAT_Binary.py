from time import perf_counter

from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.solvers import Solver

from threading import Timer

TIMEOUT_SECONDS = 180

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

        number_of_variables = self.n * self.n
        total_variables = self.vpool.top
        auxiliary_variables = total_variables - number_of_variables

        encoding_time = end_encoding - start_encoding
        loading_time = end_loading - start_loading
        solving_time = end_solving - start_solving
        total_time = encoding_time + loading_time + solving_time

        print(f"N: {self.n}")
        print(f"Primary variables: {number_of_variables}")
        print(f"Total variables: {total_variables}")
        print(f"Auxiliary variables: {auxiliary_variables}")
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
    n = 80

    problem = NQueensBinary(n)
    board = problem.solve()

    if board is not None:
        print("\nSolution:")
        problem.print_board(board)