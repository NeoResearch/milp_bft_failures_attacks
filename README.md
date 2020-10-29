# A MILP Model for Failures and Attacks on a BFT Blockchain Protocol

We present a series of MILP model for failures and attacks on a BFT blockchain protocol.

Along with the models you can find examples for generating .lp files, which can be used for typical mathematical solvers, such as CBC, GUROBI, CPLEX among others.

## Executing 

### Python-Mip (recommended - updated for both dBFT 2.0 and dBFT 3.0 proposal)

You can configure solver by modifying file directly modifying the Python file (following [python-mip guidelines](https://docs.python-mip.com])) or calling it with arguments, as detailed on the [dBFT 2.0 README](dbft2.0/README.md) or [dBFT 3.0 README](dbft3.0/README.md);

### Generating a model with AMPL (deprecated - but still works as a didatic example for dBFT 1.0, dBFT 2.0 and dBFT 3.0)

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

## Citation

Cite this in your paper as:

Vitor Nazário Coelho, Rodolfo Pereira Araujo, Haroldo Gambini Santos, Wang Yong Qiang, Igor Machado Coelho (2020). 
A MILP Model for a Byzantine Fault Tolerant Blockchain Consensus
Future Internet 2020, 12(11), 185; https://doi.org/10.3390/fi12110185

```bibtex
@article{optframe2010,
    author = {Vitor Nazário Coelho and Rodolfo Pereira Araujo and Haroldo Gambini Santos and Wang Yong Qiang and Igor Machado Coelho},
    year = {2020},
    month = {10},
    title = {A MILP Model for a Byzantine Fault Tolerant Blockchain Consensus},
    journal = "Future Internet",
    volume = 12,
    doi = "https://doi.org/10.3390/fi12110185"
}
```
