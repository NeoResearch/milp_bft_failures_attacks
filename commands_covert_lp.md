# dbft 1.0
glpsol --model MILP_BFTConsensus_dBFT1.0_Simplified.mod --data 4Nodes_TMax20.dat --wcpxlp n4-dbft1.0.lp --check && mv n4-dbft1.0.lp ../python-mip
glpsol --model MILP_BFTConsensus_dBFT1.0_Simplified.mod --data 7Nodes_TMax20.dat --wcpxlp n7-dbft1.0.lp --check && mv n7-dbft1.0.lp ../python-mip
glpsol --model MILP_BFTConsensus_dBFT1.0_Simplified.mod --data 10Nodes_TMax30.dat --wcpxlp n10.lp --check

glpsol --model MILP_BFTConsensus_dBFT1.0_Simplified_withByzantines.mod --data 4Nodes_TMax20.dat --wcpxlp n4.lp --check
glpsol --model MILP_BFTConsensus_dBFT1.0_Simplified_withByzantines.mod --data 7Nodes_TMax20.dat --wcpxlp n7.lp --check
glpsol --model MILP_BFTConsensus_dBFT1.0_Simplified_withByzantines.mod --data 10Nodes_TMax30.dat --wcpxlp n10.lp --check

# dbft 2.0

glpsol --model MILP_BFTConsensus_dBFT2.0.mod --data 4Nodes_TMax20.dat --wcpxlp n4-dbft-2.0.lp --check
glpsol --model MILP_BFTConsensus_dBFT2.0.mod --data 7Nodes_TMax20.dat --wcpxlp n7.lp --check
glpsol --model MILP_BFTConsensus_dBFT2.0.mod --data 10Nodes_TMax30.dat --wcpxlp n10.lp --check

glpsol --model MILP_BFTConsensus_dBFT2.0_withByzantines.mod --data 4Nodes_TMax20.dat --wcpxlp n4-dbft-2.0-biz.lp --check && mv n4-dbft2.0-biz.lp ../python-mip/
glpsol --model MILP_BFTConsensus_dBFT2.0_withByzantines.mod --data 7Nodes_TMax20.dat --wcpxlp n7-dbft-2.0-biz.lp --check && mv n7-dbft2.0-biz.lp ../python-mip/
glpsol --model MILP_BFTConsensus_dBFT2.0_withByzantines.mod --data 10Nodes_TMax.dat --wcpxlp n10-dbft-2.0-biz.lp --check && mv n10-dbft2.0-biz.lp ../python-mip/

glpsol --model MILP_BFTConsensus_dBFT2.0_withByzantines_liveness.mod --data 4Nodes_TMax.dat --wcpxlp n4-dbft2.0-biz-liveness.lp --check && mv n4-dbft2.0-biz-liveness.lp ../python-mip/ && (cd ../python-mip/ && python3 test-python-mip.py n4-dbft2.0-biz-liveness.lp)
glpsol --model MILP_BFTConsensus_dBFT2.0_withByzantines_liveness.mod --data 7Nodes_TMax.dat --wcpxlp n7-dbft2.0-biz-liveness.lp --check && mv n7-dbft2.0-biz-liveness.lp ../python-mip/ && (cd ../python-mip/ && python3 test-python-mip.py n7-dbft2.0-biz-liveness.lp)
glpsol --model MILP_BFTConsensus_dBFT2.0_withByzantines_liveness.mod --data 10Nodes_TMax.dat --wcpxlp n10-dbft2.0-biz-liveness.lp --check && mv n10-dbft2.0-biz-liveness.lp ../python-mip/ && (cd ../python-mip/ && python3 test-python-mip.py n10-dbft2.0-biz-liveness.lp)

# dbft 3.0

glpsol --model MILP_BFTConsensus_dBFT3.0_2P.mod --data 4Nodes_TMax20.dat --wcpxlp n4-dbft3.0-biz.lp --check && mv n4-dbft3.0-biz.lp ../python-mip/ && (cd ../python-mip/ && python3 test-python-mip.py n4-dbft3.0-biz.lp)
glpsol --model MILP_BFTConsensus_dBFT3.0_2P.mod --data 7Nodes_TMax20.dat --wcpxlp n7-dbft3.0-biz.lp --check && mv n7-dbft3.0-biz.lp ../python-mip/
glpsol --model MILP_BFTConsensus_dBFT3.0_2P.mod --data 10Nodes_TMax30.dat --wcpxlp n10-dbft3.0-biz.lp --check && mv n10-dbft3.0-biz.lp ../python-mip/


# Cplex guide

cplex
r arq.lp
o
w soln4.sol
w soln7.sol
