Here you may find two models:

1. `dbft2.0`: which is similar to the one at dBFT1.0 defined as `MILP_BFTConsensus_dBFT1.0_Simplified`

2. `dbft2.0_Byz`: which has constraints more relaxed in order to allow byzantine nodes to play with their choices. This relaxed model was also investigated for dBFT 1.0, however, due to the lack of commit phase this relaxation could easily make production of `N` spoorks (on the other hand, easily detected by the community at that time - In the best of our knowledge, any case like that ever happened on NEO network, just sporks due to network delays).

3. `dbft2.0_Byz_Liveness`: Most recent model focused on testing Liveness

# Best sol 1. and 2.

* T1 - NULL
* T2 - SEND PREPREQ
* T3 - RECEIVED PREPREQ - SEND PREPRESPONSE
* T4 - RECEIVED M PREPRESPONSE - SEND COMMIT
* T5 - RECEIVED M COMMIT - RELAYED BLOCK
