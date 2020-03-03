/* consensus replica $i$ from set of replicas R. 
$R^{BYZ}$ is byzantine set.
$R^{OK}$ is non-byzantine set. 
$R = R^{OK} \cup R^{BYZ}$, 
such that $R^{OK} \cap R^{BYZ} = \emptyset$. */

param f; /* number of faulty/Byzantine replicas. */
param N; /* total number of replicas. $N = |R| = |R^{OK}| + |R^{BYZ}| = 3f + 1$. */
param M; /* safety level. $M = 2f + 1$. */

set R := 1..N;
set R_OK := 1..M;


/* % iew $v$ from set of possible views $V$ (number of views may be limited to the number of consensus nodes $N$). $V = \{v_0, v_1, \cdots , v_{N-1}\}$ */
set V := 1..N;

/* time unit $t$ from set of discrete time units $T$.  $T = \{t_0, t_1, t_2,  \cdots \}$. */
param tMax;
set T := 1..tMax;

#param BigM;

/* ================== */
/* {DECISION VARIABLES */
var primary{R,V}, binary;
var SendPrepReq{T,R,V}, binary;
var SendPrepResp{T,R,V}, binary;
var SendCV{T,R,V}, binary;
var RecvPrepReq{T,R,R,V}, binary;
var RecvPrepResp{T,R,R,V}, binary;
var RecvChangeView{T,R,R,V}, binary;
var BlockRelay{T,R,V}, binary;
#var sentPrepReq{T,R,V}, binary;
#var sentPrepResp{T,R,V}, binary;
#var recvdPrepReq{T,R,R,V}, binary;
#var recvdPrepResp{T,R,R,V}, binary;

/* DECISION VARIABLES */
/* ================== */

/* AUXILIARY VARIABLES */
/* ================== */
var totalBlockRelayed;
var prepRespPerNodeAndView{R,V}, integer, >= 0;
var changeViewPerNodeAndView{R,V}, integer, >= 0;
var prepReqPerNodeAndView{R,V}, integer, >= 0;
var lastRelayedBlock, integer, >= 0;
var blockRelayed{V}, binary;

s.t.

/* Time zero constraints: */
initializeSendPrepareReq{i in R, v in V}: SendPrepReq[1, i, v] = 0;
initializeSendPrepareResp{i in R, v in V}: SendPrepResp[1, i, v] = 0;
initializeSendChangeView{i in R, v in V}: SendCV[1, i, v] = 0;
initializeRecvPrepareReq{i in R, j in R, v in V}: RecvPrepReq[1, i, j, v] = 0;
initializeRecvPrepareResp{i in R, j in R, v in V}: RecvPrepResp[1, i, j, v] = 0;
initializeRecvChangeView{i in R, j in R, v in V}: RecvChangeView[1, i, j, v] = 0;
initializeBlockRelay{i in R, v in V}: BlockRelay[1, i, v] = 0;
#allNodesWillBePrimary{i in R}: sum{v in V} primary[i,v] <= 1;
#t0II{i in R, v in V}: sentPrepReq[1, i, v] = 0;
#t0IV{i in R, j in R, v in V}: recvdPrepReq[1, i, j, v] = 0;
#t0VI{i in R, v in V}: sentPrepResp[1, i, v] = 0;
#t0VIII{i in R, j in R, v in V}: recvdPrepResp[1, i, j, v] = 0;

/* Prepare request constraints */
singlePrimaryEveryView{v in V}: sum{i in R} primary[i,v] <= 1;
prepReqOnlyOnce{i in R, v in V}: sum{t in T} SendPrepReq[t,i,v] <= primary[i,v];
prepReqReceivedWhenSelfSended{t in T, i in R, v in V}: RecvPrepReq[t,i,i,v] = SendPrepReq[t,i,v];
prepReqReceivedSendByJ{t in T, i in R, j in R, v in V:j!=i}: RecvPrepReq[t,i,j,v] <= sum{t2 in T: t2<t} SendPrepReq[t2,j,v];
prepReqReceivedOnlyOnce{i in R, j in R, v in V}: sum{t in T} RecvPrepReq[t,i,j,v] <= 1;
# prepReqContinousVariable{t in T, i in R, v in V: t>1}: sentPrepReq[t, i, v] = sentPrepReq[t-1, i, v] + SendPrepReq[t-1,i,v];
# prepReqReceivedContinousVariable{t in T, i in R, j in R,  v in V: t>1}: recvdPrepReq[t,i,j,v] = recvdPrepReq[t-1,i,j,v] + RecvPrepReq[t-1,i,j,v];

/* Prepare response constraints */
prepRespQuicklySendIfHonest{t in T, i in R_OK, v in V:t>1}: SendPrepResp[t,i,v] >= sum{j in R} RecvPrepReq[t-1,i,j,v];
prepRespSendOrNotIfYouAreByzantine{t in T, i in R, v in V: t>1}: SendPrepResp[t,i,v] <= sum{j in R} RecvPrepReq[t-1,i,j,v];
sendPrepResponseOnlyOnce{i in R, v in V}: sum{t in T} SendPrepResp[t,i,v] <= 1;
prepRespReceivedWhenSelfSended{t in T, i in R, v in V: t>1}: RecvPrepResp[t,i,i,v] = SendPrepResp[t,i,v];
prepRespReceivedSendByJ{t in T, i in R, j in R, v in V: t>1 and j!=i}: RecvPrepResp[t,i,j,v] <= sum{t2 in T: t2<t} SendPrepResp[t2,j,v];
receivedPrepResponseOnlyOnce{i in R, j in R, v in V}: sum{t in T} RecvPrepResp[t,i,j,v] <= 1;
# Constraint with bigM was for any prepReq
#prepRespSendIfHonest{t in T, i in R_OK, v in V:t>1}: SendPrepResp[t,i,v] * BigM >= sum{j in R} RecvPrepReq[t-1,i,j,v];
#prepRespContinousVariable{t in T, i in R, v in V: t>1}: sentPrepResp[t,i,v] = sentPrepResp[t-1,i,v] + SendPrepResp[t-1,i,v];
#prepRespVII{t in T, i in R, j in R, v in V: t>1 and j!=i}: recvdPrepResp[t,i,j,v] = recvdPrepResp[t-1,i,j,v] + RecvPrepResp[t-1,i,j,v];

/* Block relay constraints */
blockRelayIfEnoughPrepResp{t in T, i in R, v in V: t>1}: BlockRelay[t, i, v] <= (sum{t2 in T: t2<t} sum{j in R} RecvPrepResp[t2,i,j,v])/M;
blockRelayOnlyOncePerView{i in R, v in V}: sum{t in T} BlockRelay[t,i,v] <= 1;

/* Change view constraints */
sendCVOnlyOnce{i in R, v in V}: sum{t in T} SendCV[t,i,v] <= 1;
sendCVIfNotByzantineAndBlockNotRelayed{t in T, i in R_OK, v in V}: SendCV[t,i,v] <= 1 - blockRelayed[v];
changeViewReceivedWhenSelfSended{t in T, i in R, v in V: t>1}: RecvChangeView[t,i,i,v] = SendCV[t,i,v];
receivedCV{t in T, i in R, j in R, v in V: t>1 and j!=i}: RecvChangeView[t,i,j,v] = sum{t2 in T: t2<t} SendCV[t2,j,v];
receivedChangeViewOnlyOnce{i in R, j in R, v in V}: sum{t in T} RecvChangeView[t,i,j,v] <= 1;
nextPrimaryOnlyIfEnoughChangeView{i in R, v in V: v>1}: primary[i,v] <= (sum{j in R} sum{t in T} RecvChangeView[t,i,j,v-1])/M;
# Next primary only if all changeviews previous existed and were transmitted to node i
nextPrimaryOnlyIfEnoughChangeViewExisted{i in R, v in V: v>1}: primary[i,v] <= (sum{j in R} sum{t in T} sum{v2 in V: v2<v} RecvChangeView[t,i,j,v2])/(M*(v-1));
#receivePrepReq{t in T, i in R, j in R, v in V: t>1 and v>1}: RecvPrepReq[t,i,j,v] <= (sum{jj in R} RecvChangeView[t-1,i,jj,v-1])/M;

/* Calculation of auxiliary variables */
calcIfBlockRelayedOnView{v in V}: blockRelayed[v] <= sum{t in T} sum{i in R} BlockRelay[t, i, v];
calcSumBlockRelayed: totalBlockRelayed = sum{v in V} blockRelayed[v];
calcPrepResponseEveryNodeAndView{i in R, v in V}: prepRespPerNodeAndView[i,v] = (sum{j in R} sum{t in T} RecvPrepResp[t,i,j,v]);
calcChangeViewEveryNodeAndView{i in R, v in V}: changeViewPerNodeAndView[i,v] = (sum{j in R} sum{t in T} RecvChangeView[t,i,j,v]);
calcPrepReqEveryNodeAndView{i in R, v in V}: prepReqPerNodeAndView[i,v] = (sum{j in R} sum{t in T} RecvPrepReq[t,i,j,v]);
calcLastRelayedBlock{t in T, i in R, v in V}: lastRelayedBlock <= ((v-1)*tMax*BlockRelay[t,i,v] + BlockRelay[t,i,v]*t);

maximize obj: totalBlockRelayed;# * 100 + lastRelayedBlock*-1;
# +  sum{i in R}  sum{v in V} changeViewPerNodeAndView[i,v];
