from mip import *
import sys
import os.path

file_name = sys.argv[1]

#m = Model(sense=mip.MAXIMIZE) # use GRB for Gurobi
m = Model(solver_name=GUROBI)
m.SearchEmphasis = 2
m.max_gap = 0.005

m.read(file_name)
print('model has {} vars, {} constraints and {} nzs'.format(m.num_cols, m.num_rows, m.num_nz))

mip_start_filename="testToWrite.sol"
if os.path.isfile(mip_start_filename):
    print('\READING file for possible MIP_START')
    m.read(mip_start_filename)
    print('Validating mipstart {}\n\n'.format(m.validate_mip_start()))

status = m.optimize(max_seconds=600)
if status == OptimizationStatus.OPTIMAL:
    print('optimal solution cost {} found'.format(m.objective_value))
elif status == OptimizationStatus.FEASIBLE:
    print('sol.cost {} found, best possible: {}'.format(m.objective_value, m.objective_bound))
elif status == OptimizationStatus.NO_SOLUTION_FOUND:
    print('no feasible solution found, upper bound is: {}'.format(m.objective_bound))
if status == OptimizationStatus.OPTIMAL or status == OptimizationStatus.FEASIBLE:
    print('\nsolution:')
    for v in m.vars:
       if abs(v.x) > 1e-6: # only printing non-zeros
          print('{} : {}'.format(v.name, v.x))

print('\nWRITTING file possible MIP_START\n')
m.write(mip_start_filename)
    
for k in range(m.num_solutions):
    print('Solution {} with Blocks {}'.format(k, m.objective_values[k]))
#    m.sol[k].write("testToWrite{}.sol",k)
#    for (i, j) in product(range(n), range(n)):
#        if x[i][j].xi(k) >= 0.98:
#            print('\tarc ({},{})'.format(i,j))          
