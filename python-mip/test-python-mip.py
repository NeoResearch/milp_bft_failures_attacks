from mip import *
import sys

file_name = sys.argv[1]

m = Model()

m = Model(sense=mip.MAXIMIZE,solver_name=GUROBI) # use GRB for Gurobi
m.SearchEmphasis = 2
m.read(file_name)

#m.start = m.read("./test.sol")
print('model has {} vars, {} constraints and {} nzs'.format(m.num_cols, m.num_rows, m.num_nz))


m.max_gap = 0.05
m.read("testToWrite.sol")
print('validating mipstart {}'.format(m.validate_mip_start()))


status = m.optimize(max_seconds=200)
if status == OptimizationStatus.OPTIMAL:
    print('optimal solution cost {} found'.format(m.objective_value))
elif status == OptimizationStatus.FEASIBLE:
    print('sol.cost {} found, best possible: {}'.format(m.objective_value, m.objective_bound))
elif status == OptimizationStatus.NO_SOLUTION_FOUND:
    print('no feasible solution found, upper bound is: {}'.format(m.objective_bound))
if status == OptimizationStatus.OPTIMAL or status == OptimizationStatus.FEASIBLE:
    print('solution:')
    for v in m.vars:
       if abs(v.x) > 1e-6: # only printing non-zeros
          print('{} : {}'.format(v.name, v.x))

m.write("testToWrite.sol")

#m.sol.wr
          
for k in range(m.num_solutions):
    print('Solution {} with Blocks {}'.format(k, m.objective_values[k]))
#    m.sol[k].write("testToWrite{}.sol",k)
#    for (i, j) in product(range(n), range(n)):
#        if x[i][j].xi(k) >= 0.98:
#            print('\tarc ({},{})'.format(i,j))          
