# A MILP Model for Failures and Attacks on a BFT Blockchain Protocol


We present a series of MILP model for failures and attacks on a BFT blockchain protocol.

Along with the models you can find examples for generating .lp files, which can be used for typical mathematical solvers, such as CPLEX, GUROBI, among others.

If you go to folder dBFT 1.0 we suggest the following commands for converting:

```bash
glpsol --model MILP_BFTConsensus_dBFT1.0_Simplified.mod --data 4Nodes_TMax20.dat --wcpxlp n4.lp --check
glpsol --model MILP_BFTConsensus_dBFT1.0_Simplified.mod --data 7Nodes_TMax20.dat --wcpxlp n7.lp --check
glpsol --model MILP_BFTConsensus_dBFT1.0_Simplified.mod --data 10Nodes_TMax30.dat --wcpxlp n10.lp --check
```

For cplex, you can do the following:

```cplex
r n4.lp
o
w soln4.sol
```
