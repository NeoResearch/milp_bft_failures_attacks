Here you may find four models:

# Python-mip
This model is based on the [python-mip](https://github.com/coin-or/python-mip/) formulation for MILP.

Executing `python3 dbft3.0_2P.py` will run it in default mode, but some parameters can be specified as described below:

```bash
#--w1 --w2 --w3 weights
python3 dbft3.0_2P.py --minimization --w1=1000 --w2=100 --w3=0
# MINIMIZE WITH 1000 as weight for blocks and 100 for number of rounds
python3 dbft3.0_2P.py --maximization --w1=1000 --w2=-100 --w3=0
# MAXIMIZE WITH 1000 as weight for blocks and -100 for number of rounds
python3 dbft3.0_2P.py --minimization --w1=1000 --w2=100 --w3=-1
# MINIMIZE WITH 1000 as weight for blocks and 100 for number of rounds and -1 for number of msgs sent.
# In this sense, it will also try to send and receive as much message as possible

# Problem parameters:
# N(int): Defines problems param N
--N
# tMax: Defines problems param tMax
--tMax
# speedup: allows speed-up phase for skiping precommit if 2f+1 PrepRes for Priority
--speedup

# Other options are:
# generate_full_latex: defines if .pdf files will be generated (TRUE as default)
--generate_full_latex
# circle_all_send: defines if all relay messages will have a circle in the Tikz graph
--circle_all_send
# rand_pos: generates a random position in order to avoid sobreposition
--rand_pos
```
# Recommended analysis

```bash
# Maximize number of blocks, number of messages and views
python3 dbft3.0_2P.py --maximization --w1=1000 --w2=100 --w3=1 --speedup --circle_all_send --rand_pos
# Maximize number of blocks, views with minimal number of messages
python3 dbft3.0_2P.py --maximization --w1=1000 --w2=100 --w3=-1 --speedup --circle_all_send --rand_pos
# Maximize number of blocks and minimize number of views and number of messages
python3 dbft3.0_2P.py --maximization --w1=1000 --w2=-100 --w3=-1 --speedup --circle_all_send --rand_pos

```


# AMPL Model
1. `AMPL/dbft3.0_2P.mod`: A pionner model that was used to validate the proposal. However, the Python model presents a more precise model with more Honest constraints for limiting honest nodes as well as other fixes.


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
