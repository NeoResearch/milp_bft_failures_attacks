# A MILP Model for Failures and Attacks on a BFT Blockchain Protocol


We present a series of MILP model for failures and attacks on a BFT blockchain protocol.

Along with the models you can find examples for generating .lp files, which can be used for typical mathematical solvers, such as CBC, GUROBI, CPLEX among others.

## Generating a model 

If you want to generate a model for dBFT 1.0 we suggest the following commands for converting:

```bash
glpsol --model dbft1.0/dbft1.0_Simplified.mod --data ./data/4N_TMax.dat --wcpxlp n4_dbft1.0.lp --check
glpsol --model dbft1.0/dbft1.0_Simplified.mod --data ./data/7N_TMax.dat --wcpxlp n7_dbft1.0.lp --check
glpsol --model dbft1.0/dbft1.0_Simplified.mod --data ./data/10N_TMax.dat --wcpxlp n10_dbft1.0.lp --check
```

You can modify model discretization in this files `.dat`;

## Executing 

### Python-Mip

You can configure solver by modifying file `test-python-mip.py`;

`mv n4_dbft1.0.lp ./python-mip/`
`(cd python-mip && python3 test-python-mip.py n4_dbft1.0.lp)`

### Cplex 
For cplex, you can do the following:

```cplex
r n4.lp
o
w soln4.sol
```