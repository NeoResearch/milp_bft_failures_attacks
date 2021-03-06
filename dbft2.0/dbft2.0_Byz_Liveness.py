from itertools import product
from mip import Model, BINARY, INTEGER, CONTINUOUS, EQUAL, xsum, OptimizationStatus, maximize, minimize
from datetime import datetime
import sys
from pathlib import Path
sys.path.append(str(Path('.').absolute().parent))
from dbft_draw.execution_draw import is_selected, ExecutionDraw, generate_pdf_file


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


# =================== Optional Parameters  =========================
# EXAMPLES
# python3 dbft2.0_Byz_Liveness.py --minimization --w1=1000 --w2=100
# MINIMIZE WITH 1000 as weight for blocks and 100 for number of rounds
# python3 dbft2.0_Byz_Liveness.py --maximization --w1=1000 --w2=-100
# MAXIMIZE WITH 1000 as weight for blocks and -100 for number of rounds   


minimization = bool(get_args_value("minimization", True, True))
maximization = bool(get_args_value("maximization", False, True))
if maximization:
    minimization = False
#blocksWeight
blocksWeight = int(get_args_value("w1", 1000))
#numberOfRoundsWeight
numberOfRoundsWeight = int(get_args_value("w2", 100))
msgsWeight = int(get_args_value("w3", 0))


# Print all arguments
print(f'\nTotal {len(sys.argv)} and argument List: {sys.argv}')
print(f'minimization={minimization} maximization={maximization} blocksWeight={blocksWeight} numberOfRoundsWeight={numberOfRoundsWeight} msgsWeight={msgsWeight}\n')
# =================== Optional Parameters  =========================

# Total number of nodes
N = int(get_args_value("N", 4))
# number of allowed faulty nodes
f = int((N - 1) / 3)
# safe number of honest nodes
M = 2 * f + 1
# Discretization per round (view)
tMax = int(get_args_value("tMax", 8))


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


def create_decision_var_2_rv_integer(name):
    return {
        (r, v): m.add_var(f"{name}({r},{v})", var_type=INTEGER)
        for (r, v) in product(R, V)
    }

def create_decision_var_3_tiv(name):
    return {
        (t, i, v): m.add_var(f"{name}({t},{i},{v})", var_type=BINARY)
        for (t, i, v) in product(T, R, V)
    }

def create_decision_var_4_tijv(name):
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

SendPrepReq = create_decision_var_3_tiv("SendPrepReq")
SendPrepRes = create_decision_var_3_tiv("SendPrepRes")
SendCommit = create_decision_var_3_tiv("SendCommit")
SendCV = create_decision_var_3_tiv("SendCV")
BlockRelay = create_decision_var_3_tiv("BlockRelay")

RecvPrepReq = create_decision_var_4_tijv("RecvPrepReq")
RecvPrepResp = create_decision_var_4_tijv("RecvPrepResp")
RecvCommit = create_decision_var_4_tijv("RecvCommit")
RecvCV = create_decision_var_4_tijv("RecvCV")

"""
Auxiliary Variables
===================
"""
totalBlockRelayed = m.add_var("totalBlockRelayed", var_type=INTEGER)
blockRelayed = {v: m.add_var(f"blockRelayed({v})", var_type=BINARY) for v in V}
lastRelayedBlock = m.add_var("lastRelayedBlock", var_type=INTEGER)
numberOfRounds = m.add_var("numberOfRounds", var_type=INTEGER)
totalNumberSendMsg = m.add_var("totalNumberSendMsg", var_type=INTEGER)
totalNumberRcvdMsg = m.add_var("totalNumberRcvdMsg", var_type=INTEGER)
totalNumberMsgs = m.add_var("totalNumberMsgs", var_type=INTEGER)
changeViewRecvPerNodeAndView = create_decision_var_2_rv_integer("changeViewRecvPerNodeAndView")

'''
prepReqSendPerNodeAndView = create_decision_var_2_rv_integer("prepReqSendPerNodeAndView")
prepRespSendPerNodeAndView = create_decision_var_2_rv_integer("prepRespSendPerNodeAndView")
commitSendPerNodeAndView = create_decision_var_2_rv_integer("commitSendPerNodeAndView")
changeViewSendPerNodeAndView = create_decision_var_2_rv_integer("changeViewSendPerNodeAndView")
prepReqRecvPerNodeAndView = create_decision_var_2_rv_integer("prepReqRecvPerNodeAndView")
prepRespRecvPerNodeAndView = create_decision_var_2_rv_integer("prepRespRecvPerNodeAndView")
commitRecvPerNodeAndView = create_decision_var_2_rv_integer("commitRecvPerNodeAndView")
blockRelayPerNodeAndView = create_decision_var_2_rv_integer("blockRelayPerNodeAndView")
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

# Force the node to Received PrepRes along with PrepReq (in dBFT we call all as Preparation)
for (t, i, j, v) in product(T - {1}, R, R, V):
    m += (
        RecvPrepResp[t, i, j, v]
        >= RecvPrepReq[t, i, j, v],
        "prepResReceivedAlongWithPrepReq(%s,%s,%s,%s)" % (t, i, j, v),
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

"""
MARK A PAYLOAD AS RECEIVED ONLY ONCE PER VIEW
=======================
"""
for (i, j, v) in product(R, R, V):
    add_var_loop = [
        (RecvPrepReq, "rcvdPrepReqOO"),
        (RecvPrepResp, "rcvdPrepResOO"),
        (RecvCommit, "rcvdCommitOO"),
        (RecvCV, "rcvdCVOO"),
    ]
    for it in add_var_loop:
        it_var, it_name = it
        m += (
            xsum(it_var[t, i, j, v] for t in T - {1}) <= 1,
            f"{it_name}({i},{j},{v})",
        )

"""
AUXILIARY BLOCK RELAYED
=======================
"""
for (v) in V:
    m += (
        blockRelayed[v]
        <= xsum(BlockRelay[t, i, v] for t in T - {1} for i in R),
        f"blockRelayedOnlyIfNodeRelay({v})",
    )
    m += (
        blockRelayed[v] * N
        >= xsum(BlockRelay[t, i, v] for t in T - {1} for i in R),
        f"blockRelayedCounterForced({v})",
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
        add_var_loop = [
            # (RecvPrepReq, SendPrepReq, "prepReqReceivedNonByz"),
            # (RecvPrepResp, SendPrepRes, "prepRespReceivedNonByz"),
            # (RecvCommit, SendCommit, "commitReceivedNonByz"),
            # In particular, when only CV is forced, and numberrounds minimized, commits are relayed and lost.
            # On the other hand, enabling it and commits together, model can only find N rounds as minimum
            # (RecvCV, SendCV, "cvReceivedNonByz"),
        ]
        for it in add_var_loop:
            recv_var, send_var, it_name = it
            m += (
                xsum(recv_var[t, i, j, v] for t in T - {1})
                >= xsum(send_var[t, j, v] for t in T - {1}),
                f"{it_name}({i},{j},{v})",
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
    add_var_loop = [
        (SendPrepRes, RecvPrepReq, 1, 0, "assertSendPrepResWithinSimLimit"),
        (SendCommit, RecvPrepResp, 2, - M + 1, "assertSendCommitWithinSimLimit"),
        (BlockRelay, RecvCommit, 2, - M + 1, "assertBlockRelayWithinSimLimit"),
    ]
    for it in add_var_loop:
        send_var, recv_var, rate, delta, it_name = it
        m += (
            xsum(rate * send_var[t, i, v] for t in T - {1})
            >= xsum(recv_var[t, i, j, v] for (t, j) in product(T - {1}, R)) + delta,
            f"{it_name}({i},{v})",
        )

# We assume that honest nodes will only perform an action if view change was approved - no view jumps
# - not tested if really needed
for (i, v) in product(R_OK, V - {1}):
    add_var_loop = [
        (SendPrepReq, "sendPrepReqOnlyIfViewBeforeOk"),
        (SendPrepRes, "sendPrepResOnlyIfViewBeforeOk"),
        (SendCommit, "sendCommitOnlyIfViewBeforeOk"),
        (SendCV, "sendCVOnlyIfViewBeforeOk"),
    ]
    for it in add_var_loop:
        it_var, it_name = it
        m += (
            xsum(it_var[t, i, v] for t in T - {1})
            <= (1 / M) * changeViewRecvPerNodeAndView[i, v - 1],
            f"{it_name}({i},{v})",
        )

# Assert Non-byz to SendCV every round, if commit not achieved
# After first round we need to ensure circular behavior in order to not force if round is not active
for i in R_OK:
    m += (
        xsum(SendCV[t, i, 1] for t in T - {1})
        >= 1 - xsum(SendCommit[t, i, 1] for t in T - {1}),
        f"assertSendCVIfNotSendCommitV1({i})",
    )

for (i, v) in product(R_OK, V - {1}):
    m += (
        xsum(SendCV[t, i, v] for t in T - {1})
        >= 1 - xsum(SendCommit[t, i, v2] for t in T - {1} for v2 in V if v2 <= v) - (1 - xsum(Primary[ii, v - 1] for ii in R)),
        f"assertSendCVIfNotCommitAndYesPrimary({i},{v})",
    )

for (i, v, t) in product(R_OK, V, T - {1}):
    # LINKS CV AND PrepReq,PrepRes and Commit
    add_var_loop = [
        (SendPrepReq, SendCV, "noPrepReqIfCV"),
        (SendPrepRes, SendCV, "noPrepResIfCV"),
        (SendCommit, SendCV, "noCommitIfCV"),
        # LINKS Commit and LIMITS - analogous as the constrains for SendCV
        (SendCV, SendCommit, "noCVIfCommit"),
        # LINKS BlockRelayed and LIMITS - analogous as the constrains for SendCV
        (SendPrepReq, BlockRelay, "noBlockYesPrepReq"),
        (SendPrepRes, BlockRelay, "noBlockYesPrepRes"),
        (SendCommit, BlockRelay, "noBlockYesCommit"),
        (SendCV, BlockRelay, "noBlockYesCV"),
    ]
    for it in add_var_loop:
        send_var, send_var2, it_name = it
        m += (
            send_var[t, i, v]
            <= 1 - xsum(send_var2[t2, i, v] for t2 in T if 1 < t2 <= t),
            f"{it_name}({i},{v},{t})",
        )

for (i, v) in product(R_OK, V - {1}):
    # LINKS BlockRelayed and LIMITS in past views
    m += (
        Primary[i, v]
        <= 1 - xsum(BlockRelay[t, i, v2] for t in T - {1} for v2 in V if v2 < v),
        "noBlockOldViewsYesPrimary(%s,%s)" % (i, v),
    )
    add_var_loop = [
        (SendPrepReq, BlockRelay, "noBlockOldViewsYesPrepReq"),
        (SendPrepRes, BlockRelay, "noBlockOldViewsYesPrepRes"),
        (SendCommit, BlockRelay, "noBlockOldViewsYesCommit"),
        # LINKS Commit and LIMITS in past views
        (SendPrepReq, SendCommit, "noCommitOldViewsYesPrepReq"),
        (SendPrepRes, SendCommit, "noCommitOldViewsYesPrepRes"),
        (SendCommit, SendCommit, "noCommitOldViewsYesCommit"),
        (SendCV, SendCommit, "noCommitOldViewsYesCV"),
    ]
    for it in add_var_loop:
        send_var, relay_var, it_name = it
        m += (
            xsum(send_var[t, i, v] for t in T - {1})
            <= 1 - xsum(relay_var[t, i, v2] for t in T - {1} for v2 in V if v2 < v),
            f"{it_name}({i},{v})",
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
if msgsWeight != 0:
    m += totalNumberSendMsg == xsum(SendPrepReq[t, i, v] + SendPrepRes[t, i, v] + SendCommit[t, i, v] + SendCV[t, i, v]for (t, i, v) in product(T, R, V)), "calcTotalNumberOfSentMsgs"
    m += totalNumberRcvdMsg == xsum(RecvPrepReq[t, i, j, v] + RecvPrepResp[t, i, j, v] + RecvCommit[t, i, j, v] + RecvCV[t, i, j, v] for (t, i, j, v) in product(T, R, R, V)), "calcTotalNumberOfRcvdMsgs"
    m += totalNumberMsgs == totalNumberSendMsg + totalNumberRcvdMsg, "calcTotalNumberOfMsgs"

# For Minimization - Default
if minimization:
    m.objective = minimize(totalBlockRelayed * blocksWeight + numberOfRounds * numberOfRoundsWeight + msgsWeight * totalNumberMsgs)
    print(f'\nMINIMIZE with blocksWeight={blocksWeight} numberOfRoundsWeight={numberOfRoundsWeight}\n')
if not minimization:
    m.objective = maximize(totalBlockRelayed * blocksWeight + numberOfRounds * numberOfRoundsWeight + msgsWeight * totalNumberMsgs)
    print(f'MAXIMIZE with blocksWeight={blocksWeight} numberOfRoundsWeight={numberOfRoundsWeight}\n')
# OTHER POSSIBLE OJECTIVES such as counting total number of messages in order to maximize communication and conflicts
# Exponentially penalize extra view (similar to what time does to an attacker that tries to delay messages)
# m.objective = minimize(totalBlockRelayed*11111 + xsum(Primary[i, v]*10**v  for (i, v) in product(R, V)));
# m.objective = maximize(totalBlockRelayed*1000 + lastRelayedBlock*-1)

m.verbose = 1

# enter initial solution: list of pairs of (var, value)
# m.start = [
#            (Primary[1,5], 1)
#          ]

# print(f'model has {m.num_cols} vars, {m.num_rows} constraints and {m.num_nz} nzs')
nbin = len([v for v in m.vars if v.var_type == BINARY])
ncon = len([v for v in m.vars if v.var_type == CONTINUOUS])
nint = len([v for v in m.vars if v.var_type == INTEGER])
neq = len([c for c in m.constrs if c.expr.sense == EQUAL])
nineq = len([c for c in m.constrs if c.expr.sense != EQUAL])
print(
    f"model has {m.num_cols} vars ({nbin} bin, {ncon} cont and {nint} gen."
    f"integer), {m.num_rows} constraints ({neq} equalities and {nineq} "
    f"inequalities) and {m.num_nz} nzs"
)

m.write('a.lp')

status = m.optimize(max_seconds=600)

drawing_file_name = \
    f"sol" \
    f"_N_{N}_f_{f}_M_{M}_tMax_{tMax}" \
    f"_Min_{minimization}_w1_{blocksWeight}_w2_{numberOfRoundsWeight}_w3_{msgsWeight}" \
    f"_{datetime.today().strftime('%Y-%m-%d-%H:%M:%S')}"
with open(f"{drawing_file_name}.out", 'w') as sol_out:
    if status == OptimizationStatus.OPTIMAL or status == OptimizationStatus.FEASIBLE:
        sol_out.write('solution:\n')
        for v in m.vars:
            if abs(v.x) > 1e-6:  # only printing non-zeros
                sol_out.write(f'{v.name} : {v.x}\n')

    sol_out.write('\n\n========= DETAILED SOLUTION =========\n\n')
    for v in V:
        tTotal = (v - 1) * tMax
        sol_out.write(f'VIEW {v}\n')
        for i in R:
            sol_out.write(f'\tValidator {i}\n')
            if is_selected(Primary[i, v]):
                sol_out.write('\t\tPRIMARY\n')
            else:
                sol_out.write('\t\tBACKUP\n')
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
                        sol_out.write(f'\t\t\t{i} {send_name} in {t}/{t + tTotal} at {v}\n')
                    for j in R:
                        if is_selected(recv_var[t, i, j, v]):
                            counter += 1
                            sol_out.write(f'\t\t\t\t{i} {recv_name} in {t}/{t + tTotal} from {j} at {v}\n')

                if is_selected(BlockRelay[t, i, v]):
                    sol_out.write(f'\t\t\t{i} BlockRelay in {t}/{t + tTotal} at {v}\n')
            sol_out.write(
                f'\t\t\t{i} counterRcvd: PrepReq={countRecvPrepReq} PrepRes={countRecvPrepRes} '
                f'Commit={countRecvCommit} CV={countRecvCV}\n'
            )
    sol_out.write('========= DETAILED SOLUTION =========\n\n\n')

    if status == OptimizationStatus.OPTIMAL:
        sol_out.write(f'optimal solution cost {m.objective_value} found\n')
    elif status == OptimizationStatus.FEASIBLE:
        sol_out.write(f'sol.cost {m.objective_value} found, best possible: {m.objective_bound}\n')
    elif status == OptimizationStatus.NO_SOLUTION_FOUND:
        sol_out.write(f'no feasible solution found, upper bound is: {m.objective_bound}\n')

    for k in range(m.num_solutions):
        sol_out.write(f'Solution {k} with Blocks {m.objective_values[k]}\n')
    sol_out.write("\n")


with open(f"{drawing_file_name}.tex", 'w') as tex_out:
    execution_draw = ExecutionDraw(
        view_size=tMax, n=N, f=f, m=M,
        send_prep_req=SendPrepReq, send_prep_res=SendPrepRes, send_pre_commit={}, send_commit=SendCommit, send_cv=SendCV,
        recv_prep_req=RecvPrepReq, recv_prep_res=RecvPrepResp, recv_pre_commit={}, recv_commit=RecvCommit, recv_cv=RecvCV,
        primary=Primary, block_relays=BlockRelay,
    )
    view_title = bool(get_args_value("view_title", True))
    first_block = int(get_args_value("first_block", 1))
    rand_pos = bool(get_args_value("rand_pos", False, True))
    generate_full_latex = bool(get_args_value("generate_full_latex", True, True))
    circle_all_send = bool(get_args_value("circle_all_send", False, True))
    execution_draw.draw_tikzpicture(
        view_title=view_title, first_block=first_block, rand_pos=rand_pos,
        generate_full_latex=generate_full_latex, circle_all_send=circle_all_send,
        out=tex_out,
    )

generate_pdf_file(drawing_file_name)
