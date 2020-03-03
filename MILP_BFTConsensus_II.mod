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

param BigM;

/* ================== */
/* {DECISION VARIABLES */
var primary{R,V}, binary;
var SendPrepReq{T,R,V}, binary;
var SendPrepResp{T,R,V}, binary;
var RecvPrepReq{T,R,R,V}, binary;
var RecvPrepResp{T,R,R,V}, binary;
var RecvChangeView{T,R,R,V}, binary;
var BlockRelay{T,R,V}, binary;
var SendCV{T,R,V}, binary;
var sentPrepReq{T,R,V}, binary;
var sentPrepResp{T,R,V}, binary;
var recvdPrepReq{T,R,R,V}, binary;
var recvdPrepResp{T,R,R,V}, binary;
var blockRelayed{V}, binary;
/* DECISION VARIABLES} */
/* ================== */

/* Auxiliary VARIABLES} */
/* ================== */
var totalBlockRelayed;
var prepRespPerNodeAndView{R,V}, integer, >= 0;
var changeViewPerNodeAndView{R,V}, integer, >= 0;
var prepReqPerNodeAndView{R,V}, integer, >= 0;
var lastRelayedBlock, integer;

s.t.

calcSumBlockRelayed: totalBlockRelayed = sum{v in V} blockRelayed[v];


maximize obj: totalBlockRelayed * 100 + lastRelayedBlock;
# +  sum{i in R}  sum{v in V} changeViewPerNodeAndView[i,v];

/* Time zero constraints: */
singlePrimaryEveryView{v in V}: sum{i in R} primary[i,v] <= 1;
#allNodesWillBePrimary{i in R}: sum{v in V} primary[i,v] <= 1;
t0I{i in R, v in V}: SendPrepReq[1, i, v] = 0;
t0II{i in R, v in V}: sentPrepReq[1, i, v] = 0;
t0III{i in R, j in R, v in V}: RecvPrepReq[1, i, j, v] = 0;
t0IV{i in R, j in R, v in V}: recvdPrepReq[1, i, j, v] = 0;
t0V{i in R, v in V}: SendPrepResp[1, i, v] = 0;
t0VI{i in R, v in V}: sentPrepResp[1, i, v] = 0;
t0VII{i in R, j in R, v in V}: RecvPrepResp[1, i, j, v] = 0;
t0VIII{i in R, j in R, v in V}: recvdPrepResp[1, i, j, v] = 0;
t0VIV{i in R, v in V}: BlockRelay[1, i, v] = 0;
t0InitializedReceivedChangeView{i in R, j in R, v in V}: RecvChangeView[1, i, j, v] = 0;
t0InitializedReceivedChangeViewII{i in R, v in V}: SendCV[1, i, v] = 0;


/* Prepare request constraints */
prepReqOnlyOnce{i in R, v in V}: sum{t in T} SendPrepReq[t,i,v] <= primary[i,v];
prepReqContinousVariable{t in T, i in R, v in V: t>1}: sentPrepReq[t, i, v] = sentPrepReq[t-1, i, v] + SendPrepReq[t-1,i,v];
prepReqSelfSended{t in T, i in R, v in V}: RecvPrepReq[t,i,i,v] = SendPrepReq[t,i,v];
receivedPrepReqOnlyOnce{i in R, j in R, v in V}: sum{t in T} RecvPrepReq[t,i,j,v] <= 1;
prepReqReceivedIfNodeJSends{t in T, i in R, j in R, v in V:j!=i}: RecvPrepReq[t,i,j,v] <= sum{t2 in T: t2<t} SendPrepReq[t2,j,v];
# prepReqReceivedContinousVariable{t in T, i in R, j in R,  v in V: t>1}: recvdPrepReq[t,i,j,v] = recvdPrepReq[t-1,i,j,v] + RecvPrepReq[t-1,i,j,v];

/* Prepare response constraints */
prepRespSendIfHonest{t in T, i in R_OK, v in V:t>1}: SendPrepResp[t,i,v] * BigM >= sum{j in R} RecvPrepReq[t-1,i,j,v];
prepRespSendOrNotIfYouAreByzantine{t in T, i in R, v in V: t>1}: SendPrepResp[t,i,v] <= sum{j in R} RecvPrepReq[t-1,i,j,v];
prepRespOnlyOnce{i in R, v in V}: sum{t in T} SendPrepResp[t,i,v] <= 1;
#prepRespContinousVariable{t in T, i in R, v in V: t>1}: sentPrepResp[t,i,v] = sentPrepResp[t-1,i,v] + SendPrepResp[t-1,i,v];
prepRespSelfSended{t in T, i in R, v in V: t>1}: RecvPrepResp[t,i,i,v] = SendPrepResp[t,i,v];
receivedPrepResponseOnlyOnce{i in R, j in R, v in V}: sum{t in T} RecvPrepResp[t,i,j,v] <= 1;
prepRespReceivedIfNodeJSends{t in T, i in R, j in R, v in V: t>1 and j!=i}: RecvPrepResp[t,i,j,v] <= sum{t2 in T: t2<t} SendPrepResp[t2,j,v]; # sentPrepResp[t,j,v] +
#prepRespVII{t in T, i in R, j in R, v in V: t>1 and j!=i}: recvdPrepResp[t,i,j,v] = recvdPrepResp[t-1,i,j,v] + RecvPrepResp[t-1,i,j,v];

/* Block relay constraints */
blockRelayIfEnoughPrepResp{t in T, i in R, v in V: t>1}: BlockRelay[t, i, v] <= (sum{t2 in T: t2<t} sum{j in R} RecvPrepResp[t2,i,j,v])/M;
blockRelayOnlyOnce{i in R, v in V}: sum{t in T} BlockRelay[t,i,v] <= 1;
blockRelayII{v in V}: blockRelayed[v] <= sum{t in T} sum{i in R} BlockRelay[t, i, v];

/* Change view constraints */
sendCVLimit{i in R, v in V}: sum{t in T} SendCV[t,i,v] <= 1;
sendCV{t in T, i in R_OK, v in V}: SendCV[t,i,v] <= 1 - blockRelayed[v];
receivedCVSelfSended{t in T, i in R, v in V: t>1}: RecvChangeView[t,i,i,v] = SendCV[t,i,v];
receivedChangeViewOnlyOnce{i in R, j in R, v in V}: sum{t in T} RecvChangeView[t,i,j,v] <= 1;
receivedCV{t in T, i in R, j in R, v in V: t>1 and j!=i}: RecvChangeView[t,i,j,v] = sum{t2 in T: t2<t} SendCV[t2,j,v];
primaryOnNextView{i in R, v in V: v>1}: primary[i,v] <= (sum{j in R} sum{t in T} RecvChangeView[t,i,j,v-1])/M;
#receivePrepReq{t in T, i in R, j in R, v in V: t>1 and v>1}: RecvPrepReq[t,i,j,v] <= (sum{jj in R} RecvChangeView[t-1,i,jj,v-1])/M;

calcPrepResponseEveryNodeAndView{i in R, v in V}: prepRespPerNodeAndView[i,v] = (sum{j in R} sum{t in T} RecvPrepResp[t,i,j,v]);
calcChangeViewEveryNodeAndView{i in R, v in V}: changeViewPerNodeAndView[i,v] = (sum{j in R} sum{t in T} RecvChangeView[t,i,j,v]);
calcPrepReqEveryNodeAndView{i in R, v in V}: prepReqPerNodeAndView[i,v] = (sum{j in R} sum{t in T} RecvPrepReq[t,i,j,v]);
calcLastRelayedBlock{t in T, i in R, v in V}: lastRelayedBlock <= ((v-1)*tMax*BlockRelay[t,i,v] + BlockRelay[t,i,v]*t) * -1;