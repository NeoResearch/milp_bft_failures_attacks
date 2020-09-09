# A MILP Model for Failures and Attacks on a BFT Blockchain Protocol

We present a series of MILP model for failures and attacks on a BFT blockchain protocol.

Along with the models you can find examples for generating .lp files, which can be used for typical mathematical solvers, such as CBC, GUROBI, CPLEX among others.

## Executing 

### Python-Mip

You can configure solver by modifying file `dbft2.0/dbft2.0_Byz_Liveness.py` or calling with with arguments, as detailed on the [dBFT 2.0 README](dbft2.0/README.md) or [dBFT 3.0 README](dbft3.0/README.md);


### Generating a model with AMPL

If you want to generate a model for dBFT 1.0, dBFT 2.0 and dBFT 3.0 we suggest the following commands for converting (examples on dBFT 1.0):

```bash
glpsol --model dbft1.0/dbft1.0_Simplified.mod --data ./data/4N_TMax.dat --wcpxlp n4_dbft1.0.lp --check
glpsol --model dbft1.0/dbft1.0_Simplified.mod --data ./data/7N_TMax.dat --wcpxlp n7_dbft1.0.lp --check
glpsol --model dbft1.0/dbft1.0_Simplified.mod --data ./data/10N_TMax.dat --wcpxlp n10_dbft1.0.lp --check
```

You can modify model discretization in this files `.dat`;

The AMPL models have been not updated, altought they were the first to be implemented and are expected to be functional enough to be used.
In this sense, we suggest the use of the Python version created used [python-mip](https://github.com/coin-or/python-mip]) for dBFT 2.0 and 3.0.

#### Example for Cplex 
For cplex, you can do the following:

```cplex
r n4.lp
o
w soln4.sol
```