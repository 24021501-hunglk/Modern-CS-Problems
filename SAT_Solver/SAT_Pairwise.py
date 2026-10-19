from pysat.solvers import Solver
from time import perf_counter

class NQueensPairwise:
    def __init__(self, n):
        self.n = n
        self.clauses = []

    def var(self, row, col):
        return row * self.n + col + 1

    def at_least_one(self, variables):
        self.clauses.append(variables)

    def at_most_one_pairwise(self, variables):
        for i in range(len(variables)):
            for j in range(i + 1, len(variables)):
                self.clauses.append([
                    -variables[i],
                    -variables[j]
                ])

    def build(self):

        n = self.n

        for row in range(n):

            variables = [
                self.var(row, col)
                for col in range(n)
            ]

            self.at_least_one(variables)

            # At most one queen
            self.at_most_one_pairwise(variables)

        for col in range(n):

            variables = [
                self.var(row, col)
                for row in range(n)
            ]

            self.at_most_one_pairwise(variables)

        for d in range(-(n - 1), n):

            variables = []

            for row in range(n):
                col = row - d

                if 0 <= col < n:
                    variables.append(self.var(row, col))

            if len(variables) > 1:
                self.at_most_one_pairwise(variables)

        for s in range(2 * n - 1):

            variables = []

            for row in range(n):
                col = s - row

                if 0 <= col < n:
                    variables.append(self.var(row, col))

            if len(variables) > 1:
                self.at_most_one_pairwise(variables)

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
            satisfiable = solver.solve()
            end_solving = perf_counter()

            if not solver.solve():
                print("No solution.")
                return None

            model = solver.get_model()

        board = []

        for row in range(self.n):

            queen_col = None

            for col in range(self.n):

                v = self.var(row, col)

                if v in model:
                    queen_col = col
                    break

            board.append(queen_col)

        number_of_variables = self.n * self.n
        number_of_clauses = len(self.clauses)
        
        encoding_time = end_encoding - start_encoding
        loading_time = end_loading - start_loading
        solving_time = end_solving - start_solving
        total_time = encoding_time + loading_time + solving_time

        print("Number of variables:", number_of_variables)
        print("Number of clauses:", number_of_clauses)
        print(f"Encoding time: {encoding_time:.6f} seconds")
        print(f"Loading time: {loading_time:.6f} seconds")
        print(f"Solving time: {solving_time:.6f} seconds")
        print(f"Total time: {total_time:.6f} seconds")

        return board

    def print_board(self, board):

        for row in range(self.n):

            for col in range(self.n):

                if board[row] == col:
                    print("Q", end=" ")
                else:
                    print(".", end=" ")

            print()

if __name__ == "__main__":

    n = 80

    problem = NQueensPairwise(n)

    board = problem.solve()

    if board is not None:

        print(f"Solution for N = {n}")
        problem.print_board(board)

        print("\nQueen positions:")
        for row, col in enumerate(board):
            print(f"({row}, {col})")