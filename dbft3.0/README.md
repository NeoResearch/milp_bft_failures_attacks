Here you may find four models:

# Python-mip
This model is based on the [python-mip](https://github.com/coin-or/python-mip/) formulation for MILP.

Executing `python3 dbft2.0_Byz_Liveness.py` will run it in default mode.

```bash
#--w1 --w2 --w3 weights
python3 dbft3.0_2P.py --minimization --w1=1000 --w2=100 --w3=0
# MINIMIZE WITH 1000 as weight for blocks and 100 for number of rounds
python3 dbft3.0_2P.py --maximization --w1=1000 --w2=-100 --w3=0
# MAXIMIZE WITH 1000 as weight for blocks and -100 for number of rounds
python3 dbft3.0_2P.py --minimization --w1=1000 --w2=100 --w3=-1
# MINIMIZE WITH 1000 as weight for blocks and 100 for number of rounds and -1 for number of msgs sent.
# In this sense, it will also try to send and receive as much message as possible

# Other options are:
# generate_full_latex: defines if .pdf files will be generated (TRUE as default)
--generate_full_latex
# circle_all_send: defines if all relay messages will have a circle in the Tikz graph
--circle_all_send
# rand_pos: generates a random position in order to avoid sobreposition
--rand_pos
# speedup: allows speed-up phase for skiping precommit if 2f+1 PrepRes for Priority
--speedup
```


# AMPL Models
1. `dbft2.0`: which is similar to the one at dBFT1.0 defined as `MILP_BFTConsensus_dBFT1.0_Simplified`

2. `dbft2.0_Byz`: which has constraints more relaxed in order to allow byzantine nodes to play with their choices. This relaxed model was also investigated for dBFT 1.0, however, due to the lack of commit phase this relaxation could easily make production of `N` spoorks (on the other hand, easily detected by the community at that time - In the best of our knowledge, any case like that ever happened on NEO network, just sporks due to network delays).

3. `dbft2.0_Byz_Liveness`: Most recent model focused on testing Liveness


# SPEED UP FALSE (0)

* T1 - NULL
* T2 - SEND PREPREQ
* T3 - RECEIVED PREPREQ - SEND PREPRESPONSE
* T4 - RECEIVED M PREPRESPONSE P-BACKUP (2) OR F+1 FROM P-PRIORITY (1) - SEND PRECOMMIT
* T5 - RECEIVED M PRECOMMIT - SEND COMMIT
* T6 - RECEIVED M COMMIT - RELAYED BLOCK

# SPEED UP TRUE (1) - BEST CASE

* T1 - NULL
* T2 - SEND PREPREQ
* T3 - RECEIVED PREPREQ - SEND PREPRESPONSE
* T4 - RECEIVED M PREPRESPONSE P-PRIORITY (1)  - SEND COMMIT
* T5 - RECEIVED M COMMIT - RELAYED BLOCK

For using automatic graph generation with Python file install `sudo apt-get install texlive-latex-base texlive-latex-extra`
