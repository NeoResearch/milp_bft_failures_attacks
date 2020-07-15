Here you may find four models:

# Python-mip
This model is based on the [python-mip](https://github.com/coin-or/python-mip/) formulation for MILP.

Executing `python3 dbft2.0_Byz_Liveness.py` will run it in default mode.

```bash
python3 dbft2.0_Byz_Liveness.py --minimization --w1=1000 --w2=100
# MINIMIZE WITH 1000 as weight for blocks and 100 for number of rounds
python3 dbft2.0_Byz_Liveness.py --maximization --w1=1000 --w2=-100
# MAXIMIZE WITH 1000 as weight for blocks and -100 for number of rounds
# Other options are:
# generate_full_latex: defines if .pdf files will be generated (TRUE as default)
--generate_full_latex
# circle_all_send: defines if all relay messages will have a circle in the Tikz graph
--circle_all_send
# rand_pos: generates a random position in order to avoid sobreposition
--rand_pos
```


# AMPL Models
1. `dbft2.0`: which is similar to the one at dBFT1.0 defined as `MILP_BFTConsensus_dBFT1.0_Simplified`

2. `dbft2.0_Byz`: which has constraints more relaxed in order to allow byzantine nodes to play with their choices. This relaxed model was also investigated for dBFT 1.0, however, due to the lack of commit phase this relaxation could easily make production of `N` spoorks (on the other hand, easily detected by the community at that time - In the best of our knowledge, any case like that ever happened on NEO network, just sporks due to network delays).

3. `dbft2.0_Byz_Liveness`: Most recent model focused on testing Liveness

# Best sol 1. and 2.

* T1 - NULL
* T2 - SEND PREPREQ
* T3 - RECEIVED PREPREQ - SEND PREPRESPONSE
* T4 - RECEIVED M PREPRESPONSE - SEND COMMIT
* T5 - RECEIVED M COMMIT - RELAYED BLOCK

For using automatic graph generation with Python file install `sudo apt-get install texlive-latex-base texlive-latex-extra`
