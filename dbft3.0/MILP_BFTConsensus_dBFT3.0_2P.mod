param f; /* number of faulty/Byzantine replicas. */
param N; /* total number of replicas. $N = |R| = |R^{OK}| + |R^{BYZ}| = 3f + 1$. */
param M; /* safety level. $M = 2f + 1$. */

/* consensus replica $i$ from set of replicas R. 
$R^{OK}$ is non-byzantine set. 
$R = R^{OK} \cup R^{BYZ} = 1M+1..M+F$, 
such that $R^{OK} \cap R^{BYZ} = \emptyset$. */
set R := 1..N;
set R_OK := 1..M;

/* View $v$ from set of possible views $V$ (number of views may be limited to the number of consensus nodes $N$). $V = \{v_0, v_1, \cdots , v_{N-1}\}$ */
set V := 1..N;

/* Double primaries */
set P := 1..2;

/* time unit $t$ from set of discrete time units $T$.  $T = \{t_0, t_1, t_2,  \cdots \}$. */
param tMax;
set T := 1..tMax;

/* =================== */
/* {DECISION VARIABLES */
var Primary{P,R,V}, binary;
var SendPrepReq{P,T,R,V}, binary;
var SendPrepResp{P,T,R,V}, binary;
var SendPreCommit{P,T,R,V}, binary;
var SendCommit{P,T,R,V}, binary;
var SendCV{T,R,V}, binary;
/* RecvPrepReq{14,1,2,3} sinalizes that the node 1 has received a prepere_request from the node 2 during the view 3  */
var RecvPrepReq{P,T,R,R,V}, binary;
/* RecvPrepResp{18,4,5,3} sinalizes that the node 4 has received a prepere_response from the node 5 during the view 3  */
var RecvPrepResp{P,T,R,R,V}, binary;
var RecvPreCommit{P,T,R,R,V}, binary;
var RecvCommit{P,T,R,R,V}, binary;
var BlockRelay{P,T,R,V}, binary;
/* RecvCV{18,1,3,3} sinalizes that the node 1 has received a ChangeView from the node 3 during the view 3  */
var RecvCV{T,R,R,V}, binary;

/* DECISION VARIABLES} */
/* ================== */

/* ==================== */
/* {AUXILIARY VARIABLES */
var totalBlockRelayed;
var lastRelayedBlock, integer, >= 0;
var blockRelayed{P,V}, binary;
var prepReqSendPerNodeAndView{R,V}, integer, >= 0;
var prepRespSendPerNodeAndView{R,V}, integer, >= 0;
var commitSendPerNodeAndView{R,V}, integer, >= 0;
var changeViewSendPerNodeAndView{R,V}, integer, >= 0;
var prepReqRecvPerNodeAndView{R,V}, integer, >= 0;
var prepRespRecvPerNodeAndView{R,V}, integer, >= 0;
var changeViewRecvPerNodeAndView{R,V}, integer, >= 0;
var commitRecvPerNodeAndView{R,V}, integer, >= 0;
var blockRelayPerNodeAndView{R,V}, integer, >= 0;
/* AUXILIARY VARIABLES} */
/* =================== */

s.t.

/* Time zero constraints: */
initializeSendPrepareReq{p in P,i in R, v in V}: SendPrepReq[p,1, i, v] = 0;
initializeSendPrepareResp{p in P,i in R, v in V}: SendPrepResp[p,1, i, v] = 0;
initializeSendPreCommit{p in P,i in R, v in V}: SendPreCommit[p,1, i, v] = 0;
initializeSendCommit{p in P,i in R, v in V}: SendCommit[p,1, i, v] = 0;
initializeSendChangeView{i in R, v in V}: SendCV[1, i, v] = 0;
initializeRecvPrepareReq{p in P,i in R, j in R, v in V}: RecvPrepReq[p,1, i, j, v] = 0;
initializeRecvPrepareResp{p in P,i in R, j in R, v in V}: RecvPrepResp[p,1, i, j, v] = 0;
initializeRecvPreCommit{p in P,i in R, j in R, v in V}: RecvPreCommit[p,1, i, j, v] = 0;
initializeRecvCommit{p in P,i in R, j in R, v in V}: RecvCommit[p,1, i, j, v] = 0;
initializeRecvCV{i in R, j in R, v in V}: RecvCV[1, i, j, v] = 0;
initializeBlockRelay{p in P,i in R, v in V}: BlockRelay[p,1, i, v] = 0;

/* Prepare request constraints */
singlePrimary1EveryView{v in V}: sum{i in R} Primary[1,i,v] <= 1;
primary1OnlyOnce{i in R}: sum{v in V} Primary[1,i,v] <= 1;
primary2OnlyOnce{i in R}: sum{v in V} Primary[2,i,v] <= 1;
/* If backup can not help on the first view the consensus should follow its normal flow */
primary2OnlyFirstView: sum{i in R} Primary[2,i,1] <= 1;
primary20ForOtherViews: sum{v in V: v>1} sum{i in R} Primary[2,i,v] = 0;

prepReqOnlyOnce{p in P, i in R, v in V}: sum{t in T} SendPrepReq[p,t,i,v] <= Primary[p,i,v];
prepReqReceivedWhenSelfSended{p in P,t in T, i in R, v in V}: RecvPrepReq[p,t,i,i,v] = SendPrepReq[p,t,i,v];
prepReqReceivedSendByJ{p in P,t in T, i in R, j in R, v in V:j!=i}: RecvPrepReq[p,t,i,j,v] <= sum{t2 in T: t2<t} SendPrepReq[p,t2,j,v];
prepReqReceivedOnlyOnce{p in P,i in R, j in R, v in V}: sum{t in T} RecvPrepReq[p,t,i,j,v] <= 1;
# If we consider R_OK then N blocks are produced - Modify those 2 constraints below for more realistic Byzantine behavior
# sendPrepReqOnlyIfBlockNotRelayed and sendPrepReqOnlyIfViewBeforeWasAccomplished
sendPrepReqOnlyIfBlockNotRelayedInPastView{p in P,i in R, v in V: v>1}: sum{t in T} SendPrepReq[p,t,i,v] <= (1 - sum{t in T} sum{v2 in V:v2<v} BlockRelay[p,t,i,v2]);
sendPrepReqOnlyIfViewBeforeWasAccomplished{p in P,i in R, v in V: v>1}: sum{t in T} SendPrepReq[p,t,i,v] <= (sum{j in R} sum{t in T} RecvCV[t,i,j,v-1])/M;

/* Prepare response constraints */
# prepRespQuicklySendIfHonest{p in P, t in T, i in R_OK, v in V:t>1}: SendPrepResp[p,t,i,v] >= sum{j in R} RecvPrepReq[p,t-1,i,j,v];
prepRespSendOrNotIfYouAreByzantine{p in P, t in T, i in R, v in V: t>1}: SendPrepResp[p,t,i,v] <= sum{t2 in T:t2<t} sum{j in R} RecvPrepReq[p,t2,i,j,v];

# This is the trick - Most hard constraint and damage detected until now
sendPrepResponseOnlyOnceForNonByz{i in R, v in V}: sum{t in T} sum{p in P} SendPrepResp[p,t,i,v] <= 1;
sendPrepResponseOnlyOnceForAll{p in P, i in R, v in V}: sum{t in T} SendPrepResp[p,t,i,v] <= 1;

prepRespReceivedWhenSelfSended{p in P,t in T, i in R, v in V: t>1}: RecvPrepResp[p,t,i,i,v] = SendPrepResp[p,t,i,v];
prepRespReceivedSendByJ{p in P,t in T, i in R, j in R, v in V: t>1 and j!=i}: RecvPrepResp[p,t,i,j,v] <= sum{t2 in T: t2<t} SendPrepResp[p,t2,j,v];
receivedPrepResponseOnlyOnceForAnyPrimary{i in R_OK, j in R, v in V}: sum{t in T} sum{p in P} RecvPrepResp[p,t,i,j,v] <= 1;
receivedPrepResponseOnlyOnce{p in P,i in R, j in R, v in V}: sum{t in T} RecvPrepResp[p,t,i,j,v] <= 1;
# If we consider R_OK then N blocks are produced - Modify those 2 constraints below for more realistic Byzantine behavior
# sendPrepResponseOnlyIfBlockNotRelayed and sendPrepResponseOnlyIfViewBeforeWasAccomplished
sendPrepResponseOnlyIfBlockNotRelayed{p in P,i in R, v in V: v>1}: sum{t in T} SendPrepResp[p,t,i,v] <= (1 - sum{t in T} sum{v2 in V:v2<v} BlockRelay[p,t, i, v2]);
sendPrepResponseOnlyIfViewBeforeWasAccomplished{p in P,i in R, v in V: v>1}: sum{t in T} SendPrepResp[p,t,i,v] <= (sum{j in R} sum{t in T} RecvCV[t,i,j,v-1])/M;

/* Pre-Commit constraints */
preCommitQuicklySendIfHonest1{t in T, i in R, v in V:t>1}: SendPreCommit[1,t,i,v] <= (sum{t2 in T: t2<t} sum{j in R} RecvPrepResp[1,t2,i,j,v])/(f+1);
preCommitQuicklySendIfHonest2{t in T, i in R, v in V:t>1}: SendPreCommit[2,t,i,v] <= (sum{t2 in T: t2<t} sum{j in R} RecvPrepResp[2,t2,i,j,v])/(M);
#sendPreCommitOnlyOnce{i in R, v in V}: sum{t in T} sum{p in P} SendPreCommit[p,t,i,v] <= 1;
sendPreCommitOnlyOnce{p in P, i in R, v in V}: sum{t in T} SendPreCommit[p,t,i,v] <= 1;
preCommitReceivedWhenSelfSended{p in P,t in T, i in R, v in V: t>1}: RecvPreCommit[p,t,i,i,v] = SendPreCommit[p,t,i,v];
preCommitReceivedSendByJ{p in P,t in T, i in R, j in R, v in V: t>1 and j!=i}: RecvPreCommit[p,t,i,j,v] <= sum{t2 in T: t2<t} SendPreCommit[p,t2,j,v];
receivedPreCommitOnlyOnce{p in P,i in R, j in R, v in V}: sum{t in T} RecvPreCommit[p,t,i,j,v] <= 1;
sendPreCommitOnlyIfChangeViewNotSent{p in P,i in R, v in V}: sum{t in T} SendPreCommit[p,t,i,v] <= (1 - sum{t in T} SendCV[t, i, v]);
# If we consider R_OK then N blocks are produced - Modify those 2 constraints below for more realistic Byzantine behavior
# sendPrepResponseOnlyIfBlockNotRelayed and sendPrepResponseOnlyIfViewBeforeWasAccomplished
sendPreCommitOnlyIfViewBeforeWasAccomplished{p in P,i in R, v in V: v>1}: sum{t in T} SendPreCommit[p,t,i,v] <= (sum{j in R} sum{t in T} RecvCV[t,i,j,v-1])/M;
sendPreCommitOnlyIfBlockNotRelayed{p in P,i in R, v in V: v>1}: sum{t in T} SendPreCommit[p,t,i,v] <= (1 - sum{t in T} sum{v2 in V:v2<v} BlockRelay[p,t, i, v2]);

/* Commit constraints */
commitSentIfMPrepResp{p in P,t in T, i in R, v in V:t>1}: SendCommit[p,t,i,v] <= (sum{t2 in T: t2<t} sum{j in R} RecvPreCommit[p,t2,i,j,v])/M;
#sendCommitOnlyOnce{i in R, v in V}: sum{t in T} sum{p in P} SendCommit[p,t,i,v] <= 1;
sendCommitOnlyOnce{p in P, i in R, v in V}: sum{t in T} SendCommit[p,t,i,v] <= 1;
commitReceivedWhenSelfSended{p in P,t in T, i in R, v in V: t>1}: RecvCommit[p,t,i,i,v] = SendCommit[p,t,i,v];
commitReceivedSendByJ{p in P,t in T, i in R, j in R, v in V: t>1 and j!=i}: RecvCommit[p,t,i,j,v] <= sum{t2 in T: t2<t} SendCommit[p,t2,j,v];
receivedCommitOnlyOnce{p in P,i in R, j in R, v in V}: sum{t in T} RecvCommit[p,t,i,j,v] <= 1;
# If we consider R_OK then N blocks are produced - Modify those 3 constraints below for more realistic Byzantine behavior
# sendCommitOnlyIfChangeViewNotSent and sendCommitOnlyIfViewBeforeWasAccomplished and sendCommitOnlyIfBlockNotRelayed
sendCommitOnlyIfChangeViewNotSent{p in P,i in R_OK, v in V}: sum{t in T} SendCommit[p,t,i,v] <= (1 - sum{t in T} SendCV[t, i, v]);
sendCommitOnlyIfViewBeforeWasAccomplished{p in P,i in R_OK, v in V: v>1}: sum{t in T} SendCommit[p,t,i,v] <= (sum{j in R} sum{t in T} RecvCV[t,i,j,v-1])/M;
sendCommitOnlyIfBlockNotRelayed{p in P,i in R_OK, v in V: v>1}: sum{t in T} SendCommit[p,t,i,v] <= (1 - sum{t in T} sum{v2 in V:v2<v} BlockRelay[p,t, i, v2]);

/* Block relay constraints */
blockRelayIfEnoughPrepResp{p in P, t in T, i in R, v in V: t>1}: BlockRelay[p,t,i,v] <= (sum{t2 in T: t2<t} sum{j in R} RecvCommit[p,t2,i,j,v])/M;
# Even non byzantine. However, it was interesting observed that it could happen if R_OK on blockRelayLimitToOneForNonByz
blockRelayOnlyOncePerViewPerPrimaryNonByz{i in R_OK, v in V}: sum{t in T} sum{p in P} BlockRelay[p,t,i,v] <= 1;
blockRelayOnlyOncePerViewPerPrimaryForAll{p in P, i in R, v in V}: sum{t in T} BlockRelay[p,t,i,v] <= 1;
blockRelayLimitToOneForNonByz{i in R_OK}: sum{t in T} sum{v in V} sum{p in P} BlockRelay[p,t,i,v] <= 1;
#blockRelayLimitForAll{p in P, i in R}: sum{t in T} sum{v in V} BlockRelay[p,t,i,v] <= 1;

/* Change view constraints */
sendCVOnlyOnce{i in R, v in V}: sum{t in T} SendCV[t,i,v] <= 1;
changeViewReceivedWhenSelfSended{t in T, i in R, v in V: t>1}: RecvCV[t,i,i,v] = SendCV[t,i,v];
receivedCV{t in T, i in R, j in R, v in V: t>1 and j!=i}: RecvCV[t,i,j,v] = sum{t2 in T: t2<t} SendCV[t2,j,v];
receivedChangeViewOnlyOnce{i in R, j in R, v in V}: sum{t in T} RecvCV[t,i,j,v] <= 1;
nextPrimaryOnlyIfEnoughChangeView{p in P, i in R, v in V: v>1}: Primary[p,i,v] <= (sum{j in R} sum{t in T} RecvCV[t,i,j,v-1])/M;
# Next primary only if all changeviews previous existed and were transmitted to node i
nextPrimaryOnlyIfPreviousPrimary{p in P, i in R, v in V: v>1}: Primary[p,i,v] <= sum{j in R} Primary[p,j,v-1];
# Even for Byzantine node, if we consider R_OK problem become more complex. Thus, even byzantine will not cheat if relayed
# All 3 constraints below could be R_OK for more realistic scenario
# sendCVIfNonByzAndBlockNotRelayed, sendCVOnlyIfViewBeforeWasAccomplished and  nextPrimaryOnlyIfBlockNotRelayed
sendCVIfNonByzAndBlockNotRelayed{t in T, i in R_OK, v in V}: SendCV[t,i,v] <= 1 - sum{t2 in T:t2<t} sum{p in P} BlockRelay[p,t2,i,v];
sendCVOnlyIfViewBeforeWasAccomplished{i in R_OK, v in V: v>1}: sum{t in T} SendCV[t,i,v] <= (sum{j in R} sum{t in T} RecvCV[t,i,j,v-1])/M;
# Blocks relayed by other nodes can delay. In this sense, primary can start its tasks.
# That is why we use (1 - sum{t in T} sum{v2 in V:v2<v} BlockRelay[t, i,v2])
nextPrimaryOnlyIfBlockNotRelayed{p in P, i in R, v in V: v>1}: Primary[p,i,v] <= (1 - sum{t in T} sum{v2 in V:v2<v} sum{p2 in P} BlockRelay[p2,t, i,v2]);

/* Calculation of auxiliary variables */
calcIfBlockRelayedOnView{p in P, v in V}: blockRelayed[p,v] <= sum{t in T} sum{i in R} BlockRelay[p,t, i, v];
calcSumBlockRelayed: totalBlockRelayed = sum{p in P} sum{v in V} blockRelayed[p,v];
calcPrepReqSendEveryNodeAndView{i in R, v in V}: prepReqSendPerNodeAndView[i,v] = sum{t in T} sum{p in P} SendPrepReq[p,t,i,v]*t;
calcPrepRespSendEveryNodeAndView{i in R, v in V}: prepRespSendPerNodeAndView[i,v] = sum{t in T} sum{p in P} SendPrepResp[p,t,i,v]*t;
calcCommitSendEveryNodeAndView{i in R, v in V}: commitSendPerNodeAndView[i,v] = sum{t in T} sum{p in P} SendCommit[p,t,i,v]*t;
calcCVSendEveryNodeAndView{i in R, v in V}: changeViewSendPerNodeAndView[i,v] = sum{t in T} SendCV[t,i,v]*t;
calcBlockRelayEveryNodeAndView{i in R, v in V}: blockRelayPerNodeAndView[i,v] = sum{t in T} sum{p in P} BlockRelay[p,t,i,v]*t;
calcPrepReqEveryNodeAndView{i in R, v in V}: prepReqRecvPerNodeAndView[i,v] = (sum{j in R} sum{t in T} sum{p in P} RecvPrepReq[p,t,i,j,v]);
calcPrepResponseEveryNodeAndView{i in R, v in V}: prepRespRecvPerNodeAndView[i,v] = (sum{j in R} sum{t in T} sum{p in P} RecvPrepResp[p,t,i,j,v]);
calcCommitEveryNodeAndView{i in R, v in V}: commitRecvPerNodeAndView[i,v] = (sum{j in R} sum{t in T} sum{p in P} RecvCommit[p,t,i,j,v]);
calcChangeViewEveryNodeAndView{i in R, v in V}: changeViewRecvPerNodeAndView[i,v] = (sum{j in R} sum{t in T} RecvCV[t,i,j,v]);
calcLastRelayedBlock{p in P, t in T, i in R, v in V}: lastRelayedBlock >= ((v-1)*tMax*BlockRelay[p,t,i,v] + BlockRelay[p,t,i,v]*t);

#forcetotalBlockRelayed: totalBlockRelayed >= 2;

#maximize obj: totalBlockRelayed;
maximize obj: totalBlockRelayed * 1000 + lastRelayedBlock*-1;