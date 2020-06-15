#!/bin/bash

# EXAMPLES FOR CALLING
#./build_run.sh dbft2.0-liveness/dbft2.0_Byz_Liveness.mod data/4N_TMax.dat
#./build_run.sh dbft3.0/MILP_BFTConsensus_dBFT3.0_2P.mod data/4N_TMax_dbft3.0.dat

echo "Total Arguments:" $#
echo "All Arguments values:" $@

MODEL=$1
DATA=$2

echo "CREATING TEMP.LP";
glpsol --model $MODEL --data $DATA --wcpxlp temp.lp --check 

echo "MOVING TO PYTHON-MIP";
mv temp.lp ./python-mip/

echo "CALLING PYTHON-MIP";
(cd ./python-mip/ && python3 test-python-mip.py temp.lp)

echo "DELETING TEMP MODEL";
rm python-mip/temp.lp

echo "FINISHED build_run.sh script";