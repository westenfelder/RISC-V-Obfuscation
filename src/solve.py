from ortools.sat.python import cp_model
import subprocess
import sys

class Collector(cp_model.CpSolverSolutionCallback):
    def __init__(self, vars):
        super().__init__()
        self.vars, self.sols = vars, []
    def on_solution_callback(self):
        self.sols.append("".join(chr(self.Value(v) + 65) for v in self.vars))

def solve(tsum, talt, tweight, tprime, tfib, tsq):
    model = cp_model.CpModel()
    c = [model.NewIntVar(0, 30, '') for _ in range(10)] 
    p = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
    f = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55]

    # constraints
    model.Add(sum(c) == tsum)
    model.Add(sum((1 if i % 2 == 0 else -1) * c[i] for i in range(10)) == talt)
    model.Add(sum((i + 1) * c[i] for i in range(10)) == tweight)
    model.Add(sum(p[i] * c[i] for i in range(10)) == tprime)
    model.Add(sum(f[i] * c[i] for i in range(10)) == tfib)
    model.Add(sum((i + 1)**2 * c[i] for i in range(10)) == tsq)

    solver = cp_model.CpSolver()
    solver.parameters.enumerate_all_solutions = True
    cb = Collector(c)
    solver.Solve(model, cb)
    return cb.sols

if __name__ == '__main__':
    if len(sys.argv) < 7:
        print("Usage: python solve.py <sum> <alt> <weight> <prime> <fib> <sq>")
        sys.exit(1)
    
    vals = [int(x) for x in sys.argv[1:7]]
    candidates = solve(*vals)
    
    print(f"Found {len(candidates)} checksum solutions")
    solutions = []
    for candidate in candidates:
        res = subprocess.run(['./crack_x86'], input=f"{candidate}\n", text=True, capture_output=True).stdout
        if "Correct" in res:
            solutions.append(candidate)
        
    if len(solutions) != 1:
        print("ERROR: Verification Failed.")
        print("Build Failed")
    else:
        print(f"Verified: {solutions[0]}\n")
        print("Build Succeeded")
