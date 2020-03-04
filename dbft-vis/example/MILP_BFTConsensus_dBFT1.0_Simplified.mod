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

/* time unit $t$ from set of discrete time units $T$.  $T = \{t_0, t_1, t_2,  \cdots \}$. */
param tMax;
set T := 1..tMax;

/* =================== */
/* {DECISION VARIABLES */
var primary{R,V}, binary;
var SendPrepReq{T,R,V}, binary;
var SendPrepResp{T,R,V}, binary;
var SendCV{T,R,V}, binary;
var RecvPrepReq{T,R,R,V}, binary;
var RecvPrepResp{T,R,R,V}, binary;
var RecvCV{T,R,R,V}, binary;
var BlockRelay{T,R,V}, binary;
/* DECISION VARIABLES} */
/* ================== */

/* ==================== */
/* {AUXILIARY VARIABLES */
var totalBlockRelayed;
var prepReqSendPerNodeAndView{R,V}, integer, >= 0;
var prepRespSendPerNodeAndView{R,V}, integer, >= 0;
var prepRespPerNodeAndView{R,V}, integer, >= 0;
var changeViewPerNodeAndView{R,V}, integer, >= 0;
var prepReqPerNodeAndView{R,V}, integer, >= 0;
var blockRelayPerNodeAndView{R,V}, integer, >= 0;
var lastRelayedBlock, integer;
var blockRelayed{V}, binary;
/* AUXILIARY VARIABLES} */
/* =================== */

s.t.

/* Time zero constraints: */
initializeSendPrepareReq{i in R, v in V}: SendPrepReq[1, i, v] = 0;
initializeSendPrepareResp{i in R, v in V}: SendPrepResp[1, i, v] = 0;
initializeSendChangeView{i in R, v in V}: SendCV[1, i, v] = 0;
initializeRecvPrepareReq{i in R, j in R, v in V}: RecvPrepReq[1, i, j, v] = 0;
initializeRecvPrepareResp{i in R, j in R, v in V}: RecvPrepResp[1, i, j, v] = 0;
initializeRecvCV{i in R, j in R, v in V}: RecvCV[1, i, j, v] = 0;
initializeBlockRelay{i in R, v in V}: BlockRelay[1, i, v] = 0;

/* Prepare request constraints */
singlePrimaryEveryView{v in V}: sum{i in R} primary[i,v] <= 1;
primaryOnlyOnce{i in R}: sum{v in V} primary[i,v] <= 1;
prepReqOnlyOnce{i in R, v in V}: sum{t in T} SendPrepReq[t,i,v] <= primary[i,v];
prepReqReceivedWhenSelfSended{t in T, i in R, v in V}: RecvPrepReq[t,i,i,v] = SendPrepReq[t,i,v];
prepReqReceivedSendByJ{t in T, i in R, j in R, v in V:j!=i}: RecvPrepReq[t,i,j,v] <= sum{t2 in T: t2<t} SendPrepReq[t2,j,v];
prepReqReceivedOnlyOnce{i in R, j in R, v in V}: sum{t in T} RecvPrepReq[t,i,j,v] <= 1;
# If we consider R_OK then N blocks are produced - Modify those 2 constraints below for more realistic Byzantine behavior
# sendPrepReqOnlyIfBlockNotRelayed and sendPrepReqOnlyIfViewBeforeWasAccomplished
sendPrepReqOnlyIfBlockNotRelayed{i in R, v in V: v>1}: sum{t in T} SendPrepReq[t,i,v] <= (1 - sum{t in T} sum{v2 in V:v2<v} BlockRelay[t, i, v2]);
sendPrepReqOnlyIfViewBeforeWasAccomplished{i in R, v in V: v>1}: sum{t in T} SendPrepReq[t,i,v] <= (sum{j in R} sum{t in T} RecvCV[t,i,j,v-1])/M;

/* Prepare response constraints */
prepRespQuicklySendIfHonest{t in T, i in R_OK, v in V:t>1}: SendPrepResp[t,i,v] >= sum{j in R} RecvPrepReq[t-1,i,j,v];
prepRespSendOrNotIfYouAreByzantine{t in T, i in R, v in V: t>1}: SendPrepResp[t,i,v] <= sum{t2 in T:t2<t} sum{j in R} RecvPrepReq[t2,i,j,v];
sendPrepResponseOnlyOnce{i in R, v in V}: sum{t in T} SendPrepResp[t,i,v] <= 1;
prepRespReceivedWhenSelfSended{t in T, i in R, v in V: t>1}: RecvPrepResp[t,i,i,v] = SendPrepResp[t,i,v];
prepRespReceivedSendByJ{t in T, i in R, j in R, v in V: t>1 and j!=i}: RecvPrepResp[t,i,j,v] <= sum{t2 in T: t2<t} SendPrepResp[t2,j,v];
receivedPrepResponseOnlyOnce{i in R, j in R, v in V}: sum{t in T} RecvPrepResp[t,i,j,v] <= 1;
# If we consider R_OK then N blocks are produced - Modify those 2 constraints below for more realistic Byzantine behavior
# sendPrepResponseOnlyIfBlockNotRelayed and sendPrepResponseOnlyIfViewBeforeWasAccomplished
sendPrepResponseOnlyIfBlockNotRelayed{i in R, v in V: v>1}: sum{t in T} SendPrepResp[t,i,v] <= (1 - sum{t in T} sum{v2 in V:v2<v} BlockRelay[t, i, v2]);
sendPrepResponseOnlyIfViewBeforeWasAccomplished{i in R, v in V: v>1}: sum{t in T} SendPrepResp[t,i,v] <= (sum{j in R} sum{t in T} RecvCV[t,i,j,v-1])/M;

/* Block relay constraints */
blockRelayIfEnoughPrepResp{t in T, i in R, v in V: t>1}: BlockRelay[t, i, v] <= (sum{t2 in T: t2<t} sum{j in R} RecvPrepResp[t2,i,j,v])/M;
blockRelayOnlyOncePerView{i in R, v in V}: sum{t in T} BlockRelay[t,i,v] <= 1;
# Even non byzantine. However, it was interesting observed that it could happen if R_OK on blockRelayLimitToOneForNonByz
blockRelayLimitToOneForNonByz{i in R}: sum{t in T} sum{v in V} BlockRelay[t,i,v] <= 1;

/* Change view constraints */
sendCVOnlyOnce{i in R, v in V}: sum{t in T} SendCV[t,i,v] <= 1;
changeViewReceivedWhenSelfSended{t in T, i in R, v in V: t>1}: RecvCV[t,i,i,v] = SendCV[t,i,v];
receivedCV{t in T, i in R, j in R, v in V: t>1 and j!=i}: RecvCV[t,i,j,v] = sum{t2 in T: t2<t} SendCV[t2,j,v];
receivedChangeViewOnlyOnce{i in R, j in R, v in V}: sum{t in T} RecvCV[t,i,j,v] <= 1;
nextPrimaryOnlyIfEnoughChangeView{i in R, v in V: v>1}: primary[i,v] <= (sum{j in R} sum{t in T} RecvCV[t,i,j,v-1])/M;
# Next primary only if all changeviews previous existed and were transmitted to node i
nextPrimaryOnlyIfPreviousPrimary{i in R, v in V: v>1}: primary[i,v] <= sum{j in R} primary[j,v-1];
# Even for Byzantine node, if we consider R_OK problem become more complex. Thus, even byzantine will not cheat if relayed
# All 3 constraints below could be R_OK for more realistic scenario
# sendCVIfNonByzAndBlockNotRelayed, sendCVOnlyIfViewBeforeWasAccomplished and  nextPrimaryOnlyIfBlockNotRelayed
sendCVIfNonByzAndBlockNotRelayed{t in T, i in R, v in V}: SendCV[t,i,v] <= 1 - sum{t2 in T:t2<t} BlockRelay[t2,i,v];
sendCVOnlyIfViewBeforeWasAccomplished{i in R, v in V: v>1}: sum{t in T} SendCV[t,i,v] <= (sum{j in R} sum{t in T} RecvCV[t,i,j,v-1])/M;
# Blocks relayed by other nodes can delay. In this sense, primary can start its tasks.
# That is why we use (1 - sum{t in T} sum{v2 in V:v2<v} BlockRelay[t, i,v2])
nextPrimaryOnlyIfBlockNotRelayed{i in R, v in V: v>1}: primary[i,v] <= (1 - sum{t in T} sum{v2 in V:v2<v} BlockRelay[t, i,v2]);

/* Calculation of auxiliary variables */
calcIfBlockRelayedOnView{v in V}: blockRelayed[v] <= sum{t in T} sum{i in R} BlockRelay[t, i, v];
calcSumBlockRelayed: totalBlockRelayed = sum{v in V} blockRelayed[v];
calcPrepReqSendEveryNodeAndView{i in R, v in V}: prepReqSendPerNodeAndView[i,v] = sum{t in T} SendPrepReq[t,i,v];
calcPrepRespSendEveryNodeAndView{i in R, v in V}: prepRespSendPerNodeAndView[i,v] = sum{t in T} SendPrepResp[t,i,v];
calcBlockRelayEveryNodeAndView{i in R, v in V}: blockRelayPerNodeAndView[i,v] = sum{t in T} BlockRelay[t,i,v];
calcPrepResponseEveryNodeAndView{i in R, v in V}: prepRespPerNodeAndView[i,v] = (sum{j in R} sum{t in T} RecvPrepResp[t,i,j,v]);
calcChangeViewEveryNodeAndView{i in R, v in V}: changeViewPerNodeAndView[i,v] = (sum{j in R} sum{t in T} RecvCV[t,i,j,v]);
calcPrepReqEveryNodeAndView{i in R, v in V}: prepReqPerNodeAndView[i,v] = (sum{j in R} sum{t in T} RecvPrepReq[t,i,j,v]);
calcLastRelayedBlock{t in T, i in R, v in V}: lastRelayedBlock <= ((v-1)*tMax*BlockRelay[t,i,v] + BlockRelay[t,i,v]*t) * -1;

maximize obj: totalBlockRelayed;
#maximize obj: totalBlockRelayed * 100 + lastRelayedBlock;
#maximize obj: totalBlockRelayed * 100 + lastRelayedBlock +  sum{i in R} sum{v in V} changeViewPerNodeAndView[i,v];

# DEPRECATED CONSTRAINTS - ON TEST - SOON DELETED
#allNodesWillBePrimary{i in R}: sum{v in V} primary[i,v] <= 1;
#t0II{i in R, v in V}: sentPrepReq[1, i, v] = 0;
#t0IV{i in R, j in R, v in V}: recvdPrepReq[1, i, j, v] = 0;
#t0VI{i in R, v in V}: sentPrepResp[1, i, v] = 0;
#t0VIII{i in R, j in R, v in V}: recvdPrepResp[1, i, j, v] = 0;
# prepReqContinousVariable{t in T, i in R, v in V: t>1}: sentPrepReq[t, i, v] = sentPrepReq[t-1, i, v] + SendPrepReq[t-1,i,v];
# prepReqReceivedContinousVariable{t in T, i in R, j in R,  v in V: t>1}: recvdPrepReq[t,i,j,v] = recvdPrepReq[t-1,i,j,v] + RecvPrepReq[t-1,i,j,v];
#sendPrepReqOnlyIfBlockNotRelayed{t in T, i in R_OK, v in V}: SendPrepReq[t,i,v] <= 1 - sum{v2 in V: v2<v} blockRelayed[v2];
# Constraint with bigM was for any prepReq
#prepRespSendIfHonest{t in T, i in R_OK, v in V:t>1}: SendPrepResp[t,i,v] * BigM >= sum{j in R} RecvPrepReq[t-1,i,j,v];
#prepRespContinousVariable{t in T, i in R, v in V: t>1}: sentPrepResp[t,i,v] = sentPrepResp[t-1,i,v] + SendPrepResp[t-1,i,v];
#prepRespVII{t in T, i in R, j in R, v in V: t>1 and j!=i}: recvdPrepResp[t,i,j,v] = recvdPrepResp[t-1,i,j,v] + RecvPrepResp[t-1,i,j,v];

# nextPrimaryOnlyIfEnoughChangeViewExisted{i in R, v in V: v>1}: primary[i,v] <= (sum{j in R} sum{t in T} sum{v2 in V: v2<v} RecvCV[t,i,j,v2])/(M*(v-1));
#sendCVOnlyIfBlockRelayedIsSendAfter{t in T, i in R_OK, v in V}: SendCV[t,i,v] <= 1 - sum{t2 in T:t2<t} sum{j in R} BlockRelay[t2,j,v];
#sendCVIfNonByzAndBlockNotRelayed{i in R_OK, v in V: v>1}: sum{t in T} SendCV[t,i,v] <= (1 - sum{t in T} sum{v2 in V:v2<v} BlockRelay[t, i,v2]);
#sendCVIfNotByzantineAndBlockNotRelayed2{t in T, i in R_OK, v in V}: SendCV[t,i,v] <= 1 - blockRelayed[v];
#sendCVIfNotByzantineAndBlockNotRelayed{i in R_OK, v in V: v>1}: sum{t in T} SendCV[t,i,v] <= (1 - blockRelayed[v-1]);
#receivePrepReq{t in T, i in R, j in R, v in V: t>1 and v>1}: RecvPrepReq[t,i,j,v] <= (sum{jj in R} RecvCV[t-1,i,jj,v-1])/M;
