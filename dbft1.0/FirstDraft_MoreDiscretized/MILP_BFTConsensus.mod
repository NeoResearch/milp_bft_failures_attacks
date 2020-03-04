/* consensus replica $i$ from set of replicas R. 
$R^{BYZ}$ is byzantine set.
$R^{OK}$ is non-byzantine set. 
$R = R^{OK} \cup R^{BYZ}$, 
such that $R^{OK} \cap R^{BYZ} = \emptyset$. */

set R_BYZ;
set R_OK;
set R = R_OK union R_BYZ;

param f; /* number of faulty/Byzantine replicas. */
param N; /* total number of replicas. $N = |R| = |R^{OK}| + |R^{BYZ}| = 3f + 1$. */
param M = N - f; /* safety level. $M = 2f + 1$. */


/* block $b$ from set of possible proposed blocks $B$ (may be understood as block hash).  $B = \{b_0, b_1, b_2, \cdots \}$. */
set B;

/* height $h$ from set of possible heights $H$ (tests may only require two or three heights). $H = \{h_0, h_1, h_2\}$. */
set H;
/* % Igor, ainda não entendi esse height - porque não simulamos apenas para 1 height? */

/* % iew $v$ from set of possible views $V$ (number of views may be limited to the number of consensus nodes $N$). $V = \{v_0, v_1, \cdots , v_{N-1}\}$ */
set V;

/* time unit $t$ from set of discrete time units $T$.  $T = \{t_0, t_1, t_2,  \cdots \}$. */
param tMax;
set T := 1..tMax;

/* ================== */
/* {DECISION VARIABLES */
var primary{R,H,V}, binary;
var initialized{T,R,H,V}, binary;
var SendPrepReq{T,R,H,B,V}, binary;
var SendPrepResp{T,R,H,B,V}, binary;
var RecvPrepReq{T,R,R,H,B,V}, binary;
var RecvPrepResp{T,R,R,H,B,V}, binary;
var BlockRelay{T,R,H,B}, binary;
var RecvBlkPersist{T,R,R,H,B}, binary;
var sentPrepReq{T,R,H,B,V}, binary;
var sentPrepResp{T,R,H,B,V}, binary;
var recvdPrepReq{T,R,R,H,B,V}, binary;
var recvdPrepResp{T,R,R,H,B,V}, binary;
var sentBlkPersist{T,R,H,B}, binary;
var recvdBlkPersis{T,R,R,H,B}, binary;
var blockRelayed{B}, binary;
/* DECISION VARIABLES} */
/* ================== */

s.t.

calcSumBlockRelayed: totalBlockRelayed = sum{b in B} blockRelayed[b];

maximize obj: totalBlockRelayed

/* Initialization Constraints */
initializeI{i in R}: initialized[1, i, 0, 0] = 1
initializeII{i in R, h in H: h!=0, v in V: v!=0}: initialized[1, i, h, v] = 1
initializeIII{t in T: t>1, i in R, h in H: h!=0}: sum{v in V} initialized[t, i, h, v] = 1
initializeIV{t in T: t>1, i in R, v in V: h!=0}: sum{h in H} initialized[t, i, h, v] = 1

/* Time zero constraints: */
t0I{i in R, h in H, b in B, v in V}: SendPrepReq[1, i, h, b, v] = 0
t0II{i in R, h in H, b in B, v in V}: sentPrReq[1, i, h, b, v] = 0
t0III{i in R, j in R, h in H, b in B, v in V}: RecvPrepReq[1, i, j, h, b, v] = 0
t0IV{i in R, j in R, h in H, b in B, v in V}: recvdPrReq[1, i, j, h, b, v] = 0
t0V{i in R, h in H, b in B, v in V}: SendPrepResp[1, i, h, b, v] = 0
t0VI{i in R, h in H, b in B, v in V}: sentPrResp[1, i, h, b, v] = 0
t0VII{i in R, j in R, h in H, b in B, v in V}: RecvPrepResp[1, i, j, h, b, v] = 0
t0VIII{i in R, j in R, h in H, b in B, v in V}: recvdPrResp[1, i, j, h, b, v] = 0
t0VIII{i in R, h in H, b in B}: BlockRelay[1, i, h, b] = 0
t0IX{i in R, h in H, b in B}: sentBlkPersist[1, i, h, b] = 0
t0X{i in R, j in R, h in H, b in B}: RecvBlkPersist[1, i, j, h, b] = 0
t0XI{i in R, j in R, h in H, b in B}: recvdBlkPersist[1, i, j, h, b] = 0

/* Prepare request constraints */
prepReqI{t in T, i in R, h in H, b in B, v in V}: SendPrepReq[t, i, h, b, v] <= initialized[t,i,h,v]
prepReqII{t in T, i in R, h in H, b in B, v in V}: SendPrepReq[t, i, h, b, v] <= primary[i,h,v]
prepReqIII{t in T: t>1, i in R, h in H, b in B, v in V}: sentPrReq[t, i, h, b, v] = sentPrReq[t-1,h,b,v] + SendPrepReq[t-1,i,h,b,v]
prepReqIV{t in T, i in R, j in R: j!=i, h in H, b in B, v in V}: RecvPrReq[t, i, j, h, b, v] <= sentPrReq[t,j,h,b,v]
prepReqV{t in T, i in R, h in H, b in B, v in V}: RecvPrReq[t, i, i, h, b, v] = SendPrepReq[t,j,h,b,v]
prepReqVI{t in T: t>1, i in R, j in R, h in H, b in B, v in V}: recvdPrReq[t, i, j, h, b, v] = recvdPrReq[t-1,i,j,h,b,v] + RecvPrReq[t-1,i,j,h,b,v]

/* Prepare response constraints */
prepRespI{t in T: t>1, i in R, h in H, b in B, v in V}: SendPrepResp[t, i, h, b, v] <= initialized[t,i,h,v]
prepRespII{t in T: t>1, i in R_OK, h in H, b in B, v in V}: SendPrepResp[t, i, h, b, v] >= ( sum{j in R} recvdPrReq{t-1,i,j,h,b,v} )/ N
prepRespIII{t in T: t>1, i in R, h in H, b in B, v in V}: SendPrepResp[t, i, h, b, v] <= sum{j in R} recvdPrReq{t-1,i,j,h,b,v}
prepRespIV{t in T: t>1, i in R, h in H, b in B, v in V}: sentPrResp[t, i, i, h, b, v] = sentPrResp[t-1,i,h,b,v] + SendPrepResp[t-1,i,h,b,v]
prepRespV{t in T: t>1, i in R, j in R: j!=i, h in H, b in B, v in V}: RecvPrResp[t, i, j, h, b, v] <= sentPrResp[t,j,h,b,v] + SendPrepResp[t-1,i,h,b,v]
prepRespVI{t in T: t>1, i in R, j in R: j!=i, h in H, b in B, v in V}: RecvPrResp[t, i, i, h, b, v] = SendPrepResp[t,i,h,b,v]
prepRespVII{t in T: t>1, i in R, j in R: j!=i, h in H, b in B, v in V}: recvdPrResp[t, i, j, h, b, v] = recvdPrResp[t-1, i, j, h, b, v] + RecvPrResp[t-1, i, j, h, b, v]

/* Block persist constraints */
blockPersistI{t in T: t>1, i in R, h in H, b in B}: sentBlkPersist[t, i, h, b] = sentBlkPersist[t-1, i, h, b] + BlockRelay[t-1, i, h, b]
blockPersistII{t in T: t>1, i in R, j in R: j!= i, h in H, b in B}: RecvBlkPersist[t, i, j, h, b] <= sentBlkPersist[t, j, h, b]
blockPersistIII{t in T: t>1, i in R, h in H, b in B}: RecvBlkPersist[t, i, i, h, b] =  BlockRelay[t, i, h, b]
blockPersistIV{t in T: t>1, i in R, j in R, h in H, b in B}: recvdBlkPersist[t, i, j, h, b] =  recvdBlkPersist[t-1, i, j h, b] + RecvBlkPersist[t-1, i, j, h, b]


/* Block relay constraints */
blockRelayI{i in R, h in H, b in B}: sum{t in T}sentBlkPersist[t, i, h, b] <= 1
blockRelayII{b in B}: blockRelayed[b] <= (sum{t in T} sum{i in R} sum{h in H} BlockRelay[t, i, h, b]) / N
blockRelayIII{t in T, i in R, h in H, b in B}: BlockRelay[t, i, h, b] <= (sum{j in R} recvdPrResp[t-1,i,j,h,b,v])/M + sum{j in R} recvdBlkPersist[t,i,j,h,b]
