from itertools import product
from mip import Model, BINARY, INTEGER, xsum, OptimizationStatus, maximize, minimize
from execution_draw import is_selected, ExecutionDraw, generate_pdf_file
from datetime import datetime
import sys

# =================== Optional Parameters  =========================
# EXAMPLES
# python3 dbft2.0_Byz_Liveness.py 0 1000 100
# MINIMIZE WITH 1000 as weight for blocks and 100 for number of rounds
# python3 dbft2.0_Byz_Liveness.py -1 1000 -100
# MAXIMIZE WITH 1000 as weight for blocks and -100 for number of rounds

# Minimization as Default
minMax = 0
# default weight hardcoded
blocksWeight = 1000
numberOfRoundsWeight = 100


def get_args_value(name: str, default=None, is_bool: bool = False):
    if f"--{name}" in sys.argv:
        if is_bool:
            return True
        return sys.argv[sys.argv.index(f"--{name}") + 1]

    for arg in sys.argv:
        if arg.startswith(f"--{name}="):
            return arg[len(f"--{name}="):]

    if default is not None:
        return default
    if is_bool:
        return False
    return None


# Print total number of arguments
print('Total number of arguments:', format(len(sys.argv)))

# Print all arguments
print(f'Argument List: {sys.argv}')

if len(sys.argv) > 1:
    minMax = int(sys.argv[1])
    if minMax == 1:
        numberOfRoundsWeight = numberOfRoundsWeight * -1
    print('MinMax', str(minMax))
if len(sys.argv) > 2:
    blocksWeight = int(sys.argv[2])
    print('blocksWeight', str(blocksWeight))
if len(sys.argv) > 3:
    numberOfRoundsWeight = int(sys.argv[3])
    print('numberOfRoundsWeight', str(numberOfRoundsWeight))
# =================== Optional Parameters  =========================

# Total number of nodes
N = 4
# number of allowed faulty nodes
f = int((N - 1) / 3)
# safe number of honest nodes
M = 2 * f + 1
tMax = 8

print(f'Total Number of Nodes is N={N}, with f={f} and honest M={M} and tMax={tMax}\n')

# custom data can be loaded here

R = set(range(1, N + 1))
R_OK = set(range(1, M + 1))
V = set(range(1, N + 1))
T = set(range(1, tMax + 1))

# Create Model
m = Model()
m.SearchEmphasis = 2
m.max_gap = 0.005


def create_decision_var_3(name):
    return {
        (t, i, v): m.add_var(f"{name}({t},{i},{v})", var_type=BINARY)
        for (t, i, v) in product(T, R, V)
    }


def create_decision_var_4(name):
    return {
        (t, i, j, v): m.add_var(
            f"{name}({t},{i},{j},{v})", var_type=BINARY
        )
        for (t, i, j, v) in product(T, R, R, V)
    }


"""
Decision variables
==================
"""
Primary = {
    (i, v): m.add_var(f"Primary({i},{v})", var_type=BINARY)
    for (i, v) in product(R, V)
}

SendPrepReq = create_decision_var_3("SendPrepReq")
SendPrepRes = create_decision_var_3("SendPrepRes")
SendCommit = create_decision_var_3("SendCommit")
SendCV = create_decision_var_3("SendCV")
BlockRelay = create_decision_var_3("BlockRelay")

RecvPrepReq = create_decision_var_4("RecvPrepReq")
RecvPrepResp = create_decision_var_4("RecvPrepResp")
RecvCommit = create_decision_var_4("RecvCommit")
RecvCV = create_decision_var_4("RecvCV")

"""
Auxiliary Variables
===================
"""
totalBlockRelayed = m.add_var("totalBlockRelayed", var_type=INTEGER)
blockRelayed = {v: m.add_var(f"blockRelayed({v})", var_type=BINARY) for v in V}
lastRelayedBlock = m.add_var("lastRelayedBlock", var_type=INTEGER)
numberOfRounds = m.add_var("numberOfRounds", var_type=INTEGER)
changeViewRecvPerNodeAndView = {
    (r, v): m.add_var(f"changeViewRecvPerNodeAndView({r},{v})", var_type=INTEGER)
    for (r, v) in product(R, V)
}
'''
prepReqSendPerNodeAndView = {
    (r, v): m.add_var("prepReqSendPerNodeAndView(%s,%s)" % (r, v), var_type=INTEGER)
    for (r, v) in product(R, V)
}
prepRespSendPerNodeAndView = {
    (r, v): m.add_var("prepRespSendPerNodeAndView(%s,%s)" % (r, v), var_type=INTEGER)
    for (r, v) in product(R, V)
}
commitSendPerNodeAndView = {
    (r, v): m.add_var("commitSendPerNodeAndView(%s,%s)" % (r, v), var_type=INTEGER)
    for (r, v) in product(R, V)
}
changeViewSendPerNodeAndView = {
    (r, v): m.add_var("changeViewSendPerNodeAndView(%s,%s)" % (r, v), var_type=INTEGER)
    for (r, v) in product(R, V)
}
prepReqRecvPerNodeAndView = {
    (r, v): m.add_var("prepReqRecvPerNodeAndView(%s,%s)" % (r, v), var_type=INTEGER)
    for (r, v) in product(R, V)
}
prepRespRecvPerNodeAndView = {
    (r, v): m.add_var("prepRespRecvPerNodeAndView(%s,%s)" % (r, v), var_type=INTEGER)
    for (r, v) in product(R, V)
}
commitRecvPerNodeAndView = {
    (r, v): m.add_var("commitRecvPerNodeAndView(%s,%s)" % (r, v), var_type=INTEGER)
    for (r, v) in product(R, V)
}
blockRelayPerNodeAndView = {
    (r, v): m.add_var("blockRelayPerNodeAndView(%s,%s)" % (r, v), var_type=INTEGER)
    for (r, v) in product(R, V)
}
'''

"""
Time zero constraints
=====================
"""
for (i, v) in product(R, V):
    m += SendPrepReq[1, i, v] == 0, f"initSendPrepReq({i},{v})"
    m += SendPrepRes[1, i, v] == 0, f"initSendPrepRes({i},{v})"
    m += SendCommit[1, i, v] == 0, f"initSendCommit({i},{v})"
    m += SendCV[1, i, v] == 0, f"initSendCV({i},{v})"
    m += BlockRelay[1, i, v] == 0, f"initBlockRelay({i},{v})"

for (i, j, v) in product(R, R, V):
    m += RecvPrepReq[1, i, j, v] == 0, f"initRecvPrepReq({i},{j},{v})"
    m += RecvPrepResp[1, i, j, v] == 0, f"initRecvPrepRes({i},{j},{v})"
    m += RecvCommit[1, i, j, v] == 0, f"initRecvCommit({i},{j},{v})"
    m += RecvCV[1, i, j, v] == 0, f"initRecvCV({i},{j},{v})"

"""
Primary Constraints
===================
"""
# Consensus should start on the first round
m += xsum(Primary[i, 1] for i in R) == 1, "consensusShouldStart"

for v in V:
    m += xsum(Primary[i, v] for i in R) <= 1, f"singlePrimaryEveryView({v})"

for i in R:
    m += xsum(Primary[i, v] for v in V) <= 1, f"primaryOO({i})"

# Ensure circular behavior, if previous Primary not found and conclusions not done we can not move on.
# Primary should had fault, at least*/
for v in V - {1}:
    m += (
        xsum(Primary[i, v] * (v - 1) for i in R)
        <= xsum(Primary[i, v2] for i in R for v2 in V if v2 < v),
        f"avoidJumpingViews({v})",
    )

# You should proof you have certificates to be the Primary,
# proof the changeviews message records of previous view*/
for (i, v) in product(R, V - {1}):
    m += (
        Primary[i, v] <= (1 / M) * changeViewRecvPerNodeAndView[i, v - 1],
        f"nextPrimaryOnlyIfEnoughCV({i},{v})",
    )

"""
DEFINES WHEN PAYLOADS CAN BE SENDED
=======================
"""
for (t, i, v) in product(T - {1}, R, V):
    m += (
        SendPrepRes[t, i, v]
        <= xsum(RecvPrepReq[t2, i, j, v] for t2 in T if t2 <= t for j in R),
        f"prepRespSendOptionally({t},{i},{v})",
    )
    m += (
        SendCommit[t, i, v]
        <= (1 / M) * xsum(RecvPrepResp[t2, i, j, v] for t2 in T if t2 <= t for j in R),
        f"commitSentIfMPrepRespOptionally({t},{i},{v})",
    )
    m += (
        BlockRelay[t, i, v]
        <= (1 / M) * xsum(RecvCommit[t2, i, j, v] for t2 in T if t2 <= t for j in R),
        f"blockRelayOptionallyOnlyIfEnoughCommits({t},{i},{v})",
    )

"""
SEND PAYLOAD ONLY ONCE (PrepReq,PrepRes,Commit,CV,Block)
===========================
"""
for (i, v) in product(R, V):
    # Note PrepReq deals with Primary, thus, it also ensures single PreReq and discard any other except from Primary
    m += (
        xsum(SendPrepReq[t, i, v] for t in T - {1}) <= Primary[i, v],
        f"prepReqOOIfPrimary({i},{v})",
    )
    add_var_loop = [
        (SendPrepRes, "sendPrepResOO"),
        (SendCommit, "sendCommitOO"),
        (SendCV, "sendCVOO"),
        (BlockRelay, "blockRelayOO"),
    ]
    for it in add_var_loop:
        it_var, it_name = it
        m += (
            xsum(it_var[t, i, v] for t in T - {1}) <= 1,
            f"{it_name}({i},{v})",
        )

"""
DEFINE WHEN A NODE CAN REGISTER PAYLOAD AS RECEIVED (PrepReq,PrepRes,Commit and CV)
=======================
"""
# Self Sended
for (t, i, v) in product(T - {1}, R, V):
    add_var_loop = [
        (RecvPrepReq, SendPrepReq, "prepReqReceivedSS"),
        (RecvPrepResp, SendPrepRes, "prepRespReceivedSS"),
        (RecvCommit, SendCommit, "commitReceivedSS"),
        (RecvCV, SendCV, "cvReceivedSS"),
    ]
    for it in add_var_loop:
        recv_var, send_var, it_name = it
        m += (
            recv_var[t, i, i, v] == send_var[t, i, v],
            f"{it_name}({t},{i},{v})",
        )

# Sended by another node J will lag, at least, one interval `t`

for t, i, j, v in product(T - {1}, R, R, V):
    if i != j:
        add_var_loop = [
            (RecvPrepReq, SendPrepReq, "prepReqReceived"),
            (RecvPrepResp, SendPrepRes, "prepRespReceived"),
            (RecvCommit, SendCommit, "commitReceived"),
            (RecvCV, SendCV, "cvReceived"),
        ]
        for it in add_var_loop:
            recv_var, send_var, it_name = it
            m += (
                recv_var[t, i, j, v]
                <= xsum(send_var[t2, j, v] for t2 in T if 1 < t2 < t),
                f"{it_name}({t},{i},{j},{v})",
            )

# Force the node to Received PrepRes & PrepReq along with CV
# This will help nodes to propose the same block on next view
# This is currently not active on NEO dBFT 2.0
"""
for t, i, j, v in product(T - {1}, R, R_OK, V):        
        # Or you received PrepRes before or together with RecvCV
        m += (
            xsum(RecvPrepResp[t2, i, j, v] for t2 in T if 1 < t2 <= t)
            >= xsum(SendPrepRes[t2, j, v] for t2 in T if 1 < t2 < t) - (1-RecvCV[t, i, j, v])*(sum(1 for t2 in T if 1 < t2 < t)) ,
            "forcePrepResInformationonCVIfSendedByJ(%s,%s,%s,%s)" % (t, i, j, v),
        )
        m += (
            xsum(RecvPrepReq[t2, i, j, v] for t2 in T if 1 < t2 <= t)
            >= xsum(SendPrepReq[t2, j, v] for t2 in T if 1 < t2 < t) - (1-RecvCV[t, i, j, v])*(sum(1 for t2 in T if 1 < t2 < t)) ,
            "forcePrepResInformationonCVIfSendedByJ(%s,%s,%s,%s)" % (t, i, j, v),
        )
"""

# Force the node to Received PrepRes along with PrepReq
for (t, i, j, v) in product(T - {1}, R, R, V):
    m += (
        RecvPrepResp[t, i, j, v]
        >= RecvPrepReq[t, i, j, v],
        "prepResReceivedAlongWithPrepReq(%s,%s,%s,%s)" % (t, i, j, v),
    )

"""
MARK A PAYLOAD AS RECEIVED ONLY ONCE PER VIEW
=======================
"""
for (i, j, v) in product(R, R, V):
    m += (
        xsum(RecvPrepReq[t, i, j, v] for t in T - {1}) <= 1,
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
        )'''
        m += (
            xsum(RecvCommit[t, i, j, v] for t in T - {1})
            >= xsum(SendCommit[t, j, v] for t in T - {1}),
            "commitReceivedNonByz(%s,%s,%s)" % (i, j, v),
        )
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
        xsum(2 * Primary[ii, v] for ii in R)
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
        <= (1 / M) * changeViewRecvPerNodeAndView[i, v - 1],
        "sendPrepReqOnlyIfViewBeforeOk(%s,%s)" % (i, v),
    )
    m += (
        xsum(SendPrepRes[t, i, v] for t in T - {1})
        <= (1 / M) * changeViewRecvPerNodeAndView[i, v - 1],
        "sendPrepResOnlyIfViewBeforeOk(%s,%s)" % (i, v),
    )
    m += (
        xsum(SendCommit[t, i, v] for t in T - {1})
        <= (1 / M) * changeViewRecvPerNodeAndView[i, v - 1],
        "sendCommitOnlyIfViewBeforeOk(%s,%s)" % (i, v),
    )
    m += (
        xsum(SendCV[t, i, v] for t in T - {1})
        <= (1 / M) * changeViewRecvPerNodeAndView[i, v - 1],
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
        >= 1 - xsum(SendCommit[t, i, v2] for t in T - {1} for v2 in V if v2 <= v) - (1 - xsum(Primary[ii, v - 1] for ii in R)),
        "assertSendCVIfNotCommitAndYesPrimary(%s,%s)" % (i, v),
    )

for (i, v, t) in product(R_OK, V, T - {1}):
    # LINKS CV AND PrepReq,PrepRes and Commit
    m += (
        SendPrepReq[t, i, v]
        <= 1 - xsum(SendCV[t2, i, v] for t2 in T if 1 < t2 <= t),
        "noPrepReqIfCV(%s,%s,%s)" % (i, v, t),
    )
    m += (
        SendPrepRes[t, i, v]
        <= 1 - xsum(SendCV[t2, i, v] for t2 in T if 1 < t2 <= t),
        "noPrepResIfCV(%s,%s,%s)" % (i, v, t),
    )
    m += (
        SendCommit[t, i, v]
        <= 1 - xsum(SendCV[t2, i, v] for t2 in T if 1 < t2 <= t),
        "noCommitIfCV(%s,%s,%s)" % (i, v, t),
    )
    # LINKS Commit and LIMITS - analogous as the constrains for SendCV
    m += (
        SendCV[t, i, v]
        <= 1 - xsum(SendCommit[t2, i, v] for t2 in T if 1 < t2 <= t),
        "noCVIfCommit(%s,%s,%s)" % (i, v, t),
    )
    # LINKS BlockRelayed and LIMITS - analogous as the constrains for SendCV
    m += (
        SendPrepReq[t, i, v]
        <= 1 - xsum(BlockRelay[t2, i, v] for t2 in T if 1 < t2 <= t),
        "noBlockYesPrepReq(%s,%s,%s)" % (i, v, t),
    )
    m += (
        SendPrepRes[t, i, v]
        <= 1 - xsum(BlockRelay[t2, i, v] for t2 in T if 1 < t2 <= t),
        "noBlockYesPrepRes(%s,%s,%s)" % (i, v, t),
    )
    m += (
        SendCommit[t, i, v]
        <= 1 - xsum(BlockRelay[t2, i, v] for t2 in T if 1 < t2 <= t),
        "noBlockYesCommit(%s,%s,%s)" % (i, v, t),
    )
    m += (
        SendCV[t, i, v]
        <= 1 - xsum(BlockRelay[t2, i, v] for t2 in T if 1 < t2 <= t),
        "noBlockYesCV(%s,%s,%s)" % (i, v, t),
    )

for (i, v) in product(R_OK, V - {1}):
    # LINKS BlockRelayed and LIMITS in past views
    m += (
        Primary[i, v]
        <= 1 - xsum(BlockRelay[t, i, v2] for t in T - {1} for v2 in V if v2 < v),
        "noBlockOldViewsYesPrimary(%s,%s)" % (i, v),
    )
    m += (
        xsum(SendPrepReq[t, i, v] for t in T - {1})
        <= 1 - xsum(BlockRelay[t, i, v2] for t in T - {1} for v2 in V if v2 < v),
        "noBlockOldViewsYesPrepReq(%s,%s)" % (i, v),
    )
    m += (
        xsum(SendPrepRes[t, i, v] for t in T - {1})
        <= 1 - xsum(BlockRelay[t, i, v2] for t in T - {1} for v2 in V if v2 < v),
        "noBlockOldViewsYesPrepRes(%s,%s)" % (i, v),
    )
    m += (
        xsum(SendCommit[t, i, v] for t in T - {1})
        <= 1 - xsum(BlockRelay[t, i, v2] for t in T - {1} for v2 in V if v2 < v),
        "noBlockOldViewsYesCommit(%s,%s)" % (i, v),
    )
    # LINKS Commit and LIMITS in past views
    m += (
        xsum(SendPrepReq[t, i, v] for t in T - {1})
        <= 1 - xsum(SendCommit[t, i, v2] for t in T - {1} for v2 in V if v2 < v),
        "noCommitOldViewsYesPrepReq(%s,%s)" % (i, v),
    )
    m += (
        xsum(SendPrepRes[t, i, v] for t in T - {1})
        <= 1 - xsum(SendCommit[t, i, v2] for t in T - {1} for v2 in V if v2 < v),
        "noCommitOldViewsYesPrepRes(%s,%s)" % (i, v),
    )
    m += (
        xsum(SendCommit[t, i, v] for t in T - {1})
        <= 1 - xsum(SendCommit[t, i, v2] for t in T - {1} for v2 in V if v2 < v),
        "noCommitOldViewsYesCommit(%s,%s)" % (i, v),
    )
    m += (
        xsum(SendCV[t, i, v] for t in T - {1})
        <= 1 - xsum(SendCommit[t, i, v2] for t in T - {1} for v2 in V if v2 < v),
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
    numberOfRounds == xsum(Primary[i, v] for (i, v) in product(R, V)),
    "calcTotalPrimaries",
)

for (i, v) in product(R, V):
    m += (
        changeViewRecvPerNodeAndView[i, v]
        == xsum(RecvCV[t, i, j, v] for (t, j) in product(T, R)),
        "calcChangeViewEveryNodeAndView(%s,%s)" % (i, v),
    )

for (t, i, v) in product(T, R, V):
    m += (
        lastRelayedBlock
        >= ((v - 1) * tMax * BlockRelay[t, i, v] + BlockRelay[t, i, v] * t),
        "calcLastRelayedBlockMaxProblem(%s,%s,%s)" % (t, i, v),
    )

"""
OBJ FUNCTION
=======================
"""

# For Minimization - Default
if not minMax:
    m.objective = minimize(totalBlockRelayed * blocksWeight + numberOfRounds * numberOfRoundsWeight)
    print(f'\nMINIMIZE with blocksWeight={blocksWeight} numberOfRoundsWeight={numberOfRoundsWeight}\n')
if minMax:
    m.objective = maximize(totalBlockRelayed * blocksWeight + numberOfRounds * numberOfRoundsWeight)
    print(f'MAXIMIZE with blocksWeight={blocksWeight} numberOfRoundsWeight={numberOfRoundsWeight}\n')
# Exponentially penalize extra view (similar to what time does to an attacker that tries to delay messages)
# m.objective = minimize(totalBlockRelayed*11111 + xsum(Primary[i, v]*10**v  for (i, v) in product(R, V)));

# For Maximization
# m.objective = maximize(totalBlockRelayed*1000 + numberOfRounds*-1)
# m.objective = maximize(totalBlockRelayed*1000 + lastRelayedBlock*-1)

m.verbose = 1

# enter initial solution: list of pairs of (var, value)
# m.start = [
#            (Primary[1,5], 1)
#
#          ]

print(f'model has {m.num_cols} vars, {m.num_rows} constraints and {m.num_nz} nzs')

m.write('a.lp')

status = m.optimize(max_seconds=600)

drawing_file_name = \
    f"sol" \
    f"_N_{N}_f_{f}_M_{M}_tMax_{tMax}" \
    f"_MinMax_{minMax}_blocksWeight_{blocksWeight}_numberOfRoundsWeight_{numberOfRoundsWeight}" \
    f"_{datetime.today().strftime('%Y-%m-%d-%H:%M:%S')}"
with open(f"{drawing_file_name}.out", 'w') as sol_out:
    if status == OptimizationStatus.OPTIMAL or status == OptimizationStatus.FEASIBLE:
        sol_out.write('\nsolution:')
        for v in m.vars:
            if abs(v.x) > 1e-6:  # only printing non-zeros
                sol_out.write(f'{v.name} : {v.x}')

    sol_out.write('\n\n========= DETAILED SOLUTION =========')
    for v in V:
        tTotal = (v - 1) * tMax
        sol_out.write(f'VIEW {v}')
        for i in R:
            sol_out.write(f'\tValidator {i}')
            if is_selected(Primary[i, v]):
                sol_out.write('\t\tPRIMARY')
            else:
                sol_out.write('\t\tBACKUP')
            countRecvPrepReq = countRecvPrepRes = countRecvCommit = countRecvCV = 0
            for t in T:
                print_loop = [
                    ("SendPrepReq", SendPrepReq, "RecvPrepReq", RecvPrepReq, countRecvPrepReq),
                    ("SendPrepRes", SendPrepRes, "RecvPrepResp", RecvPrepResp, countRecvPrepRes),
                    ("SendCommit", SendCommit, "RecvCommit", RecvCommit, countRecvCommit),
                    ("SendCV", SendCV, "RecvCV", RecvCV, countRecvCV),
                ]
                for it in print_loop:
                    send_name, send_var, recv_name, recv_var, counter = it
                    if is_selected(send_var[t, i, v]):
                        sol_out.write(f'\t\t\t{i} {send_name} in {t}/{t + tTotal} at {v}')
                    for j in R:
                        if is_selected(recv_var[t, i, j, v]):
                            counter += 1
                            sol_out.write(f'\t\t\t\t{i} {recv_name} in {t}/{t + tTotal} from {j} at {v}')

                if is_selected(BlockRelay[t, i, v]):
                    sol_out.write(f'\t\t\t{i} BlockRelay in {t}/{t + tTotal} at {v}')
            sol_out.write(
                f'\t\t\t{i} counterRcvd: PrepReq={countRecvPrepReq} PrepRes={countRecvPrepRes} '
                f'Commit={countRecvCommit} CV={countRecvCV}'
            )
    sol_out.write('========= DETAILED SOLUTION =========\n\n')

    if status == OptimizationStatus.OPTIMAL:
        sol_out.write(f'optimal solution cost {m.objective_value} found')
    elif status == OptimizationStatus.FEASIBLE:
        sol_out.write(f'sol.cost {m.objective_value} found, best possible: {m.objective_bound}')
    elif status == OptimizationStatus.NO_SOLUTION_FOUND:
        sol_out.write(f'no feasible solution found, upper bound is: {m.objective_bound}')

    for k in range(m.num_solutions):
        sol_out.write(f'Solution {k} with Blocks {m.objective_values[k]}')
    sol_out.write("\n")


with open(f"{drawing_file_name}.tex", 'w') as tex_out:
    execution_draw = ExecutionDraw(
        tMax, N, f, M,
        SendPrepReq, SendPrepRes, SendCommit, SendCV,
        RecvPrepReq, RecvPrepResp, RecvCommit, RecvCV,
        Primary, BlockRelay
    )
    view_title = bool(get_args_value("view_title", True))
    first_block = int(get_args_value("first_block", 1))
    rand_pos = bool(get_args_value("rand_pos", False))
    generate_full_latex = bool(get_args_value("generate_full_latex", True))
    circle_all_send = bool(get_args_value("circle_all_send", False))
    execution_draw.draw_tikzpicture(
        view_title=view_title, first_block=first_block, rand_pos=rand_pos,
        generate_full_latex=generate_full_latex, circle_all_send=circle_all_send,
        out=tex_out,
    )

generate_pdf_file(drawing_file_name)
