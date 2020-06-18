from itertools import product
from mip import Model, BINARY, INTEGER, xsum, OptimizationStatus, maximize, minimize
# Total number of nodes
N = 4
# number of allowed faulty nodes
f = int((N-1)/3)
# safe number of honest nodes
M = 2*f+1
tMax = 8

# custom data can be loaded here

R = set(range(1, N + 1))
R_OK = set(range(1, M + 1))
V = set(range(1, N + 1))
T = set(range(1, tMax + 1))

m = Model()
m.SearchEmphasis = 2
m.max_gap = 0.005

"""
Decision variables
==================
"""
Primary = {
    (r, v): m.add_var("Primary(%s,%s)" % (r, v), var_type=BINARY)
    for (r, v) in product(R, V)
}
SendPrepReq = {
    (t, r, v): m.add_var("SendPrepReq(%s,%s,%s)" % (t, r, v), var_type=BINARY)
    for (t, r, v) in product(T, R, V)
}
SendPrepRes = {
    (t, r, v): m.add_var("SendPrepRes(%s,%s,%s)" % (t, r, v), var_type=BINARY)
    for (t, r, v) in product(T, R, V)
}
SendCommit = {
    (t, r, v): m.add_var("SendCommit(%s,%s,%s)" % (t, r, v), var_type=BINARY)
    for (t, r, v) in product(T, R, V)
}
SendCV = {
    (t, r, v): m.add_var("SendCV(%s,%s,%s)" % (t, r, v), var_type=BINARY)
    for (t, r, v) in product(T, R, V)
}
BlockRelay = {
    (t, r, v): m.add_var("BlockRelay(%s,%s,%s)" % (t, r, v), var_type=BINARY)
    for (t, r, v) in product(T, R, V)
}
RecvPrepReq = {
    (t, r1, r2, v): m.add_var(
        "RecvPrepReq(%s,%s,%s,%s)" % (t, r1, r2, v), var_type=BINARY
    )
    for (t, r1, r2, v) in product(T, R, R, V)
}
RecvPrepResp = {
    (t, r1, r2, v): m.add_var(
        "RecvPrepResp(%s,%s,%s,%s)" % (t, r1, r2, v), var_type=BINARY,
    )
    for (t, r1, r2, v) in product(T, R, R, V)
}
RecvCommit = {
    (t, r1, r2, v): m.add_var(
        "RecvCommit(%s,%s,%s,%s)" % (t, r1, r2, v), var_type=BINARY
    )
    for (t, r1, r2, v) in product(T, R, R, V)
}
RecvCV = {
    (t, r1, r2, v): m.add_var("RecvCV(%s,%s,%s,%s)" % (t, r1, r2, v), var_type=BINARY)
    for (t, r1, r2, v) in product(T, R, R, V)
}

"""
Auxiliary Variables
===================
"""
totalBlockRelayed = m.add_var("totalBlockRelayed", var_type=INTEGER)
blockRelayed = {v: m.add_var("blockRelayed(%s)" % v, var_type=BINARY) for v in V}
lastRelayedBlock = m.add_var("lastRelayedBlock", var_type=INTEGER)
numberOfRounds = m.add_var("numberOfRounds", var_type=INTEGER)
prepReqSendPerNodeAndView = {
    (r, v): m.add_var("prepReqSendPerNodeAndView(%d,%d)" % (r, v), var_type=INTEGER)
    for (r, v) in product(R, V)
}
prepRespSendPerNodeAndView = {
    (r, v): m.add_var("prepRespSendPerNodeAndView(%d,%d)" % (r, v), var_type=INTEGER)
    for (r, v) in product(R, V)
}
commitSendPerNodeAndView = {
    (r, v): m.add_var("commitSendPerNodeAndView(%d,%d)" % (r, v), var_type=INTEGER)
    for (r, v) in product(R, V)
}
changeViewSendPerNodeAndView = {
    (r, v): m.add_var("changeViewSendPerNodeAndView(%d,%d)" % (r, v), var_type=INTEGER)
    for (r, v) in product(R, V)
}
prepReqRecvPerNodeAndView = {
    (r, v): m.add_var("prepReqRecvPerNodeAndView(%d,%d)" % (r, v), var_type=INTEGER)
    for (r, v) in product(R, V)
}
prepRespRecvPerNodeAndView = {
    (r, v): m.add_var("prepRespRecvPerNodeAndView(%d,%d)" % (r, v), var_type=INTEGER)
    for (r, v) in product(R, V)
}
changeViewRecvPerNodeAndView = {
    (r, v): m.add_var("changeViewRecvPerNodeAndView(%d,%d)" % (r, v), var_type=INTEGER)
    for (r, v) in product(R, V)
}
commitRecvPerNodeAndView = {
    (r, v): m.add_var("commitRecvPerNodeAndView(%d,%d)" % (r, v), var_type=INTEGER)
    for (r, v) in product(R, V)
}
blockRelayPerNodeAndView = {
    (r, v): m.add_var("blockRelayPerNodeAndView(%d,%d)" % (r, v), var_type=INTEGER)
    for (r, v) in product(R, V)
}

"""
Time zero constraints
=====================
"""
for (i, v) in product(R, V):
    m += SendPrepReq[(1, i, v)] == 0, "initSendPrepReq(%s,%s)" % (i, v)
    m += SendPrepRes[1, i, v] == 0, "initSendPrepRes(%d,%d)" % (i, v)
    m += SendCommit[1, i, v] == 0, "initSendCommit(%s,%s)" % (i, v)
    m += SendCV[1, i, v] == 0, "initSendCV(%s,%s)" % (i, v)
    m += BlockRelay[1, i, v] == 0, "initBlockRelay(%s,%s)" % (i, v)

for (i, j, v) in product(R, R, V):
    m += RecvPrepReq[(1, i, j, v)] == 0, "initRecvPrepReq(%s,%s,%s)" % (i, j, v)
    m += RecvPrepResp[1, i, j, v] == 0, "initRecvPrepRes(%s,%s,%d)" % (i, j, v)
    m += RecvCommit[1, i, j, v] == 0, "initRecvCommit(%s,%s, %s)" % (i, j, v)
    m += RecvCV[1, i, j, v] == 0, "initRecvCV(%s,%s,%s)" % (i, j, v)   

"""
Primary Constraints
===================
"""
# Consensus should start on the first round
m += xsum(Primary[i, 1] for i in R) == 1, "consensusShouldStart"

for v in V:
    m += xsum(Primary[i, v] for i in R) <= 1, "singlePrimaryEveryView(%s)" % v

for i in R:
    m += xsum(Primary[i, v] for v in V) <= 1, "primaryOO(%s)" % i

# Ensure circular behavior, if previous Primary not found and conclusions not done we can not move on. 
# Primary should had fault, at least*/
for v in V - {1}:
    m += (
        xsum(Primary[i, v] * (v - 1) for i in R)
        <= xsum(Primary[i, v2] for i in R for v2 in V if v2 < v),
        "avoidJumpingViews(%s)" % v,
    )

# You should proof you have certificates to be the Primary, 
# proof the changeviews message records of previous view*/
for (i, v) in product(R, V - {1}):
    m += (
        Primary[i, v] <= changeViewRecvPerNodeAndView[i, v - 1] / M,
        "nextPrimaryOnlyIfEnoughCV(%s,%s)" % (i, v),
    )

"""
DEFINES WHEN PAYLOADS CAN BE SENDED
=======================
"""
for (t, i, v) in product(T - {1}, R, V):  
    m += (
        SendPrepRes[t, i, v]
        <= xsum(RecvPrepReq[t2, i, j, v] for t2 in T if t2 <= t for j in R),
        "prepRespSendOptionally(%s,%s,%s)" % (t, i, v),
    )
    m += (
        SendCommit[t, i, v]
        <= (1 / M) * xsum(RecvPrepResp[t2, i, j, v] for t2 in T if t2 <= t for j in R),
        "commitSentIfMPrepRespOptionally(%s,%s,%s)" % (t, i, v),
    )    
    m += (
        BlockRelay[t, i, v]
        <= (1 / M) * xsum(RecvCommit[t2, i, j, v] for t2 in T if t2 <= t for j in R),
        "blockRelayOptionallyOnlyIfEnoughCommits(%s,%s,%s)" % (t, i, v),
    )
    
"""
SEND PAYLOAD ONLY ONCE (PrepReq,PrepRes,Commit,CV,Block)
===========================
"""
for (i, v) in product(R, V):
    # Note PrepReq deals with Primary, thus, it also ensures single PreReq and discard any other except from Primary   
    m += (
        xsum(SendPrepReq[t, i, v] for t in T - {1}) <= Primary[i, v],
        "prepReqOOJustPrimary(%s,%s)" % (i, v),
    )
    m += (
        xsum(SendPrepRes[t, i, v] for t in T - {1}) <= 1,
        "sendPrepResOO(%s,%s)" % (i, v),
    )
    m += (
        xsum(SendCommit[t, i, v] for t in T - {1}) <= 1,
        "sendCommitOO(%s,%s)" % (i, v),
    )
    m += (
        xsum(SendCV[t, i, v] for t in T - {1}) <= 1,
        "sendCVOO(%s,%s)" % (i, v),
    )
    m += (
        xsum(BlockRelay[t, i, v] for t in T - {1}) <= 1,
        "blockRelayOO(%s,%s)" % (i, v),
    )           



"""
DEFINE WHEN A NODE CAN REGISTER PAYLOAD AS RECEIVED (PrepReq,PrepRes,Commit and CV)
=======================
"""
# Self Sended
for (t, i, v) in product(T - {1}, R, V):
    m += (
        RecvPrepReq[t, i, i, v] == SendPrepReq[t, i, v],
        "prepReqReceivedSS(%s,%s,%s)" % (t, i, v),
    )
    m += (
        RecvPrepResp[t, i, i, v] == SendPrepRes[t, i, v],
        "prepRespReceivedSS(%s,%s,%s)" % (t, i, v),
    )
    m += (
        RecvCommit[t, i, i, v] == SendCommit[t, i, v],
        "commitReceivedSS(%s,%s,%s)" % (t, i, v),
    )
    m += (
        RecvCV[t, i, i, v] == SendCV[t, i, v],
        "cvReceivedSS(%s,%s,%s)" % (t, i, v),
    ) 

# Sended by another node J will lag, at least, one interval `t`
for (t, i, j, v) in product(T - {1}, R, R, V):
    if j != i:
        m += (
            (
                RecvPrepReq[t, i, j, v]
                <= xsum(SendPrepReq[t2, j, v] for t2 in T if 1 < t2 < t),
            ),
            "prepReqReceived(%s,%s,%s,%d)" % (t, i, j, v),
        )
        m += (
            (
                RecvPrepResp[t, i, j, v]
                <= xsum(SendPrepRes[t2, j, v] for t2 in T if 1 < t2 < t),
            ),
            "prepRespReceived(%s,%s,%s,%s)" % (t, i, j, v),
        )
        m += (
            (
                RecvCommit[t, i, j, v]
                <= xsum(SendCommit[t2, j, v] for t2 in T if 1 < t2 < t),
            ),
            "commitReceived(%s,%s,%s,%d)" % (t, i, j, v),
        )
        m += (
            (
                RecvCV[t, i, j, v]
                <= xsum(SendCV[t2, j, v] for t2 in T if 1 < t2 < t),
            ),
            "cvReceived(%s,%s,%s,%s)" % (t, i, j, v),
        )      

# Force the node to Received PrepRes along with PrepReq
for (t, i, j, v) in product(T - {1}, R, R, V):
    m += (
         (
            RecvPrepResp[t, i, j, v]
            >= RecvPrepReq[t, i, j, v],
          ),
         "prepResReceivedAlongWithPrepReq(%s,%s,%s,%s)" % (t, i, j, v),
    )  

"""
MARK A PAYLOAD AS RECEIVED ONLY ONCE PER VIEW
=======================
"""
for (i, j, v) in product(R, R, V):
    m += (
        xsum(RecvPrepReq[t, i, j, v] for t in T -  {1}) <= 1,
        "rcvdPrepReqOO(%s,%s,%s)" % (i, j, v),
    )
    m += (
        xsum(RecvPrepResp[t, i, j, v] for t in T - {1}) <= 1,
        "rcvdPrepResOO(%s,%s,%s)" % (i, j, v),
    )    
    m += (
        xsum(RecvCommit[t, i, j, v] for t in T - {1}) <= 1,
        "rcvdCommitOO(%s,%s,%s)" % (i, j, v),
    )
    m += (
        xsum(RecvCV[t, i, j, v] for t in T - {1}) <= 1,
        "rcvdCVOO(%s,%s,%s)" % (i, j, v),
    ) 


"""
AUXILIARY BLOCK RELAYED
=======================
"""
for (v) in V:
    m += (
        blockRelayed[v] 
        <= xsum(BlockRelay[t, i, v] for t in T - {1} for i in R),
        "blockRelayedOnlyIfNodeRelay(%s)" % (v),
    )
    m += (
        blockRelayed[v] * N 
        >= xsum(BlockRelay[t, i, v] for t in T - {1} for i in R),
        "blockRelayedCounterForced(%s)" % (v),
    )      


"""
Honest Node Constraints
=======================
"""

# ----- Force nodes to receive if comes from Honest --- 
# These 4 following constraints force that payloads will arrive within the simulation limits of a given view for NonByz
# Which is not completelly correct.
# Note that, if all are enabled together they force 1 block as minimum
# consequently, addding a constraint `totalBlockRelayed = 0` makes MILP infeasible or unbounded 
for (i, j, v) in product(R_OK, R_OK, V): 
    if i != j:
        '''m += (
            xsum(RecvPrepReq[t, i, j, v] for t in T - {1})
            >= xsum(SendPrepReq[t, j, v] for t in T - {1}),
            "prepReqReceivedNonByz(%s,%s,%s)" % (i, j, v),
        )
        m += (
            xsum(RecvPrepResp[t, i, j, v] for t in T - {1})
            >= xsum(SendPrepRes[t, j, v] for t in T - {1}),
            "prepRespReceivedNonByz(%s,%s,%s)" % (i, j, v),
        )
        m += (
            xsum(RecvCommit[t, i, j, v] for t in T - {1})
            >= xsum(SendCommit[t, j, v] for t in T - {1}),
            "commitReceivedNonByz(%s,%s,%s)" % (i, j, v),
        )   '''     
    # In particular, when only CV is forced, and numberrounds minimized, commits are relayed and lost.
    # On the other hand, enabling it and commits together, model can only find N rounds as minimum                     
        m += (
            xsum(RecvCV[t, i, j, v] for t in T - {1})
            >= xsum(SendCV[t, j, v] for t in T - {1}),
            "cvReceivedNonByz(%s,%s,%s)" % (i, j, v),
        )

# Non-byz will not relay more than a single block. Byz can Relay (HOLD) and never arrive
for i in R_OK:
    m += (
        xsum(BlockRelay[t, i, v] for t in T - {1} for v in V) <= 1,
        "blockRelayLimitToOneForNonByz(%s)" % (i),
    )

# Force a Primary to exist if any honest knows change views - 2 acts as BIGNUM
for (i, v) in product(R_OK, V - {1}):
    m += (
        xsum(Primary[ii, v] for ii in R) * 2
        >= changeViewRecvPerNodeAndView[i, v - 1] - M + 1,
        "assertAtLeastOnePrimaryIfEnoughCV(%s,%s)" % (i, v),
    )

# We assume that honest nodes will perform an action within the simulation limits
for (i, v) in product(R_OK, V):
    m += (
        xsum(SendPrepReq[t, i, v] for t in T - {1}) 
        >= Primary[i, v],
        "assertSendPrepReqWithinSimLimit(%s,%s)" % (i, v),
    )
    m += (
        xsum(SendPrepRes[t, i, v] for t in T - {1})
        >= xsum(RecvPrepReq[t, i, j, v] for (t, j) in product(T - {1}, R)),
        "assertSendPrepResWithinSimLimit(%s,%s)" % (i, v),
    )
    m += (
        xsum(2 * SendCommit[t, i, v] for t in T - {1})
        >= xsum(RecvPrepResp[t, i, j, v] for (t, j) in product(T - {1}, R)) - M + 1,
        "assertSendCommitWithinSimLimit(%s,%s)" % (i, v),
    )
    m += (
        xsum(2 * BlockRelay[t, i, v] for t in T - {1})
        >= xsum(RecvCommit[t, i, j, v] for (t, j) in product(T - {1}, R)) - M + 1,
        "assertBlockRelayWithinSimLimit(%s,%s)" % (i, v),
    )

# We assume that honest nodes will only perform an action if view change was approved - no view jumps 
# - not tested if really needed 
for (i, v) in product(R_OK, V - {1}):
    m += (
        xsum(SendPrepReq[t, i, v] for t in T - {1}) 
        <= changeViewRecvPerNodeAndView[i, v - 1] / M,
        "sendPrepReqOnlyIfViewBeforeOk(%s,%s)" % (i, v),
    )
    m += (
        xsum(SendPrepRes[t, i, v] for t in T - {1}) 
        <= changeViewRecvPerNodeAndView[i, v - 1] / M,
        "sendPrepResOnlyIfViewBeforeOk(%s,%s)" % (i, v),
    )
    m += (
        xsum(SendCommit[t, i, v] for t in T - {1}) 
        <= changeViewRecvPerNodeAndView[i, v - 1] / M,
        "sendCommitOnlyIfViewBeforeOk(%s,%s)" % (i, v),
    )
    m += (
        xsum(SendCV[t, i, v] for t in T - {1}) 
        <= changeViewRecvPerNodeAndView[i, v - 1] / M,
        "sendCVOnlyIfViewBeforeOk(%s,%s)" % (i, v),
    )            

# Assert Non-byz to SendCV every round, if commit not achieved 
# After first round we need to ensure circular behavior in order to not force if round is not active 
for i in R_OK:
    m += (
        xsum(SendCV[t, i, 1] for t in T - {1}) 
        >= 1 - xsum(SendCommit[t, i, 1] for t in T - {1}),
        "assertSendCVIfNotSendCommitV1(%s)" % (i),
    )

for (i, v) in product(R_OK, V - {1}):    
    m += (
        xsum(SendCV[t, i, v] for t in T - {1}) 
        >= 1 - xsum(SendCommit[t, i, v - 1] for t in T - {1}) - (1 - xsum(Primary[ii, v - 1] for ii in R)),
        "assertSendCVIfNotCommitAndYesPrimary(%s,%s)" % (i, v),
    )

for (i, v, t) in product(R_OK, V, T - {1}): 
    # LINKS CV AND PrepReq,PrepRes and Commit
    m += (
        SendPrepReq[t, i, v] 
        <= 1 - xsum(SendCV[t2, j, v] for t2 in T if 1 < t2 <= t),
        "noPrepReqIfCV(%s,%s,%s)" % (i, v, t),
    )
    m += (
        SendPrepRes[t, i, v] 
        <= 1 - xsum(SendCV[t2, j, v] for t2 in T if 1 < t2 <= t),
        "noPrepResIfCV(%s,%s,%s)" % (i, v, t),
    )
    m += (
        SendCommit[t, i, v] 
        <= 1 - xsum(SendCV[t2, j, v] for t2 in T if 1 < t2 <= t),
        "noCommitIfCV(%s,%s,%s)" % (i, v, t),
    )
    # LINKS Commit and LIMITS - analogous as the constrains for SendCV
    m += (
        SendCV[t, i, v] 
        <= 1 - xsum(SendCommit[t2, j, v] for t2 in T if 1 < t2 <= t),
        "noCVIfCommit(%s,%s,%s)" % (i, v, t),
    ) 
    # LINKS BlockRelayed and LIMITS - analogous as the constrains for SendCV
    m += (
        SendPrepReq[t, i, v] 
        <= 1 - xsum(BlockRelay[t2, j, v] for t2 in T if 1 < t2 <= t),
        "noBlockYesPrepReq(%s,%s,%s)" % (i, v, t),
    ) 
    m += (
        SendPrepRes[t, i, v] 
        <= 1 - xsum(BlockRelay[t2, j, v] for t2 in T if 1 < t2 <= t),
        "noBlockYesPrepRes(%s,%s,%s)" % (i, v, t),
    ) 
    m += (
        SendCommit[t, i, v] 
        <= 1 - xsum(BlockRelay[t2, j, v] for t2 in T if 1 < t2 <= t),
        "noBlockYesCommit(%s,%s,%s)" % (i, v, t),
    )      
    m += (
        SendCV[t, i, v] 
        <= 1 - xsum(BlockRelay[t2, j, v] for t2 in T if 1 < t2 <= t),
        "noBlockYesCV(%s,%s,%s)" % (i, v, t),
    )                     

for (i, v) in product(R_OK, V - {1}):
    # LINKS BlockRelayed and LIMITS in past views
    m += (
        Primary[i, v] 
        <= 1 - xsum(BlockRelay[t, i, v2] for t in T - {1} for v2 in V if 1 < v2 < v),
        "noBlockOldViewsYesPrimary(%s,%s)" % (i, v),
    )
    m += (
        xsum(SendPrepReq[t, i, v] for t in T - {1})
        <= 1 - xsum(BlockRelay[t, i, v2] for t in T - {1} for v2 in V if 1 < v2 < v),
        "noBlockOldViewsYesPrepReq(%s,%s)" % (i, v),
    )
    m += (
        xsum(SendPrepRes[t, i, v] for t in T - {1})
        <= 1 - xsum(BlockRelay[t, i, v2] for t in T - {1} for v2 in V if 1 < v2 < v),
        "noBlockOldViewsYesPrepRes(%s,%s)" % (i, v),
    )
    m += (
        xsum(SendCommit[t, i, v] for t in T - {1})
        <= 1 - xsum(BlockRelay[t, i, v2] for t in T - {1} for v2 in V if 1 < v2 < v),
        "noBlockOldViewsYesCommit(%s,%s)" % (i, v),
    ) 
    # LINKS Commit and LIMITS in past views 
    m += (
        xsum(SendPrepReq[t, i, v] for t in T - {1})
        <= 1 - xsum(SendCommit[t, i, v2] for t in T - {1} for v2 in V if 1 < v2 < v),
        "noCommitOldViewsYesPrepReq(%s,%s)" % (i, v),
    )
    m += (
        xsum(SendPrepRes[t, i, v] for t in T - {1})
        <= 1 - xsum(SendCommit[t, i, v2] for t in T - {1} for v2 in V if 1 < v2 < v),
        "noCommitOldViewsYesPrepRes(%s,%s)" % (i, v),
    )
    m += (
        xsum(SendCommit[t, i, v] for t in T - {1})
        <= 1 - xsum(SendCommit[t, i, v2] for t in T - {1} for v2 in V if 1 < v2 < v),
        "noCommitOldViewsYesCommit(%s,%s)" % (i, v),
    )
    m += (
        xsum(SendCV[t, i, v] for t in T - {1})
        <= 1 - xsum(SendCommit[t, i, v2] for t in T - {1} for v2 in V if 1 < v2 < v),
        "noCommitOldViewsYesCV(%s,%s)" % (i, v),
    )                 

"""
CALCULATION OF AUXILIARY VARIABLES
=======================
"""

m += (
        totalBlockRelayed == xsum(blockRelayed[v] for v in V),
        "calcSumBlockRelayed",
    )

m += (
        numberOfRounds == xsum(Primary[i, v] for (i, v) in product(R,V)),
        "calcTotalPrimaries",
    )

for (i, v) in product(R, V):
    m += (
        changeViewRecvPerNodeAndView[i, v]
        == xsum(RecvCV[t, i, j, v] for t in T for j in R),
        "calcChangeViewEveryNodeAndView(%s,%s)" % (i, v),
    )  

"""
OBJ FUNCTION
=======================
"""

# For Minimization
m.objective = minimize(totalBlockRelayed*1000 + numberOfRounds*100);

# For Maximization
# m.objective = maximize(totalBlockRelayed*1000 + numberOfRounds);

m.verbose = 1

# enter initial solution: list of pairs of (var, value)
#m.start = [  
#            (Primary[1,5], 1)
#
#          ]

print("model now has %d variables and %d constraints" % (m.num_cols, m.num_rows))

status = m.optimize(max_seconds=600)

#if Primary[1, 5].xn(1)  >= 0.99 

if status == OptimizationStatus.OPTIMAL or status == OptimizationStatus.FEASIBLE:
    print('\nsolution:')
    for v in m.vars:
       if abs(v.x) > 1e-6: # only printing non-zeros
          print('{} : {}'.format(v.name, v.x))

if status == OptimizationStatus.OPTIMAL:
    print('optimal solution cost {} found'.format(m.objective_value))
elif status == OptimizationStatus.FEASIBLE:
    print('sol.cost {} found, best possible: {}'.format(m.objective_value, m.objective_bound))
elif status == OptimizationStatus.NO_SOLUTION_FOUND:
    print('no feasible solution found, upper bound is: {}'.format(m.objective_bound))          
