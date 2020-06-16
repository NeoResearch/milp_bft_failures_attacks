param f; /* number of faulty/Byzantine replicas. */
param N; /* total number of replicas. $N = |R| = |R^{OK}| + |R^{BYZ}| = 3f + 1$. */
param M; /* safety level. $M = 2f + 1$. */

/* consensus replica $i$ from set of replicas R. 
$R^{OK}$ is non-byzantine set. 
$R = R^{OK} \cup R^{BYZ} = 1M+1..M+F$, 
such that $R^{OK} \cap R^{BYZ} = \emptyset$.
However, R_BYZ is not used since there are not specific constraints for byzantine. 
Maybe it can be simplified in some cases.
*/
set R := 1..N;
set R_OK := 1..M;
#set R_BYZ := M..N;

/* View $v$ from set of possible views $V$ 
Thus, in this model, number of views is limited to the number of consensus nodes $N$.
$V = \{v_0, v_1, \cdots , v_{N-1}\}$ */
set V := 1..N;

/* time unit $t$ from set of discrete time units $T$.  $T = \{t_0, t_1, t_2,  \cdots \}$. */
param tMax;
set T := 1..tMax;

/* =================== */
/* {DECISION VARIABLES */
var Primary{R,V}, binary;
var SendPrepReq{T,R,V}, binary;
var SendPrepRes{T,R,V}, binary;
var SendCommit{T,R,V}, binary;
var SendCV{T,R,V}, binary;
var BlockRelay{T,R,V}, binary;
/* RecvPrepReq{14,1,2,3} sinalizes that the node 1 has received a prepere_request from the node 2 during the view 3  */
var RecvPrepReq{T,R,R,V}, binary;
var RecvPrepResp{T,R,R,V}, binary;
var RecvCommit{T,R,R,V}, binary;
var RecvCV{T,R,R,V}, binary;
/* DECISION VARIABLES} */
/* ================== */

/* ==================== */
/* {AUXILIARY VARIABLES */
var totalBlockRelayed;
var lastRelayedBlock, integer, >= 0;
var numberOfRounds, integer, >= 0;
var blockRelayed{V}, binary;
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
initializeSendPrepareReq{i in R, v in V}: SendPrepReq[1, i, v] = 0;
initializeRecvPrepareReq{i in R, j in R, v in V}: RecvPrepReq[1, i, j, v] = 0;
initializeSendPrepareResp{i in R, v in V}: SendPrepRes[1, i, v] = 0;
initializeRecvPrepareResp{i in R, j in R, v in V}: RecvPrepResp[1, i, j, v] = 0;
initializeSendCommit{i in R, v in V}: SendCommit[1, i, v] = 0;
initializeRecvCommit{i in R, j in R, v in V}: RecvCommit[1, i, j, v] = 0;
initializeSendChangeView{i in R, v in V}: SendCV[1, i, v] = 0;
initializeRecvCV{i in R, j in R, v in V}: RecvCV[1, i, j, v] = 0;
initializeBlockRelay{i in R, v in V}: BlockRelay[1, i, v] = 0;

/* ============== Primary constraints ============== */
# Consensus should start on the first round
consensusShouldStart: sum{i in R} Primary[i,1] = 1;
singlePrimaryEveryView{v in V}: sum{i in R} Primary[i,v] <= 1;
primaryOnlyOnce{i in R}: sum{v in V} Primary[i,v] <= 1;
/* Ensure circular behavior, if previous Primary not found and conclusions not done we can not move on. 
Primary should had fault, at least*/
avoidJumpingViews{v in V: v>1}: sum{i in R} Primary[i,v]*(v-1) <= sum{v2 in V:v2<v} sum{i in R} Primary[i,v2];
/* You should proof you have certificates to be the Primary, 
proof the changeviews message records of previous view*/
nextPrimaryOnlyIfEnoughCV{i in R, v in V: v>1}: Primary[i,v] <= changeViewRecvPerNodeAndView[i,v-1]/M;
/* ============== Primary constraints ============== */

/* ============== Prepare request constraints ============== */
# --------- General comments -------------
# Ensure single PreReq and discard any other except from Primary
# PrepRequest Received instantaneously when Self Sended (SS)
# Only Recv if it was sended before, otherwise it is infeasible
# --------- General comments -------------
prepReqOnlyOnceAndSentOptionally{i in R, v in V}: sum{t in T} SendPrepReq[t,i,v] <= Primary[i,v];
prepReqReceivedSS{t in T, i in R, v in V: t>1}: RecvPrepReq[t,i,i,v] = SendPrepReq[t,i,v];
prepReqReceived{t in T, i in R, j in R, v in V: t>1 and j!=i}: RecvPrepReq[t,i,j,v] <= sum{t2 in T: t2<t and t2>1} SendPrepReq[t2,j,v];
prepReqReceivedOnlyOnce{i in R, j in R, v in V}: sum{t in T} RecvPrepReq[t,i,j,v] <= 1;
/* ============== Prepare request constraints finished ==============*/

/* ============== Prepare response constraints ==============*/
sendPrepResonseOnlyOnce{i in R, v in V}: sum{t in T} SendPrepRes[t,i,v] <= 1;
prepRespSendOptionally{t in T, i in R, v in V: t>1}: SendPrepRes[t,i,v] <= sum{t2 in T:t2<=t} sum{j in R} RecvPrepReq[t2,i,j,v];
prepRespReceivedSS{t in T, i in R, v in V: t>1}: RecvPrepResp[t,i,i,v] = SendPrepRes[t,i,v];
prepRespReceived{t in T, i in R, j in R, v in V: t>1 and j!=i}: RecvPrepResp[t,i,j,v] <= sum{t2 in T: t2<t and t2>1} SendPrepRes[t2,j,v];
receivedPrepResponseOnlyOnce{i in R, j in R, v in V}: sum{t in T} RecvPrepResp[t,i,j,v] <= 1;
/* ============== Prepare response constraints finished ==============*/

/* ============== Commit constraints ============== */
sendCommitOnlyOnce{i in R, v in V}: sum{t in T} SendCommit[t,i,v] <= 1;
commitSentIfMPrepRespOptionally{t in T, i in R, v in V: t>1}: SendCommit[t,i,v] <= (sum{t2 in T: t2<=t} sum{j in R} RecvPrepResp[t2,i,j,v])/M;
commitReceivedSS{t in T, i in R, v in V: t>1}: RecvCommit[t,i,i,v] = SendCommit[t,i,v];
commitReceived{t in T, i in R, j in R, v in V: t>1 and j!=i}: RecvCommit[t,i,j,v] <= sum{t2 in T: t2<t and t2>1} SendCommit[t2,j,v];
receivedCommitOnlyOnce{i in R, j in R, v in V}: sum{t in T} RecvCommit[t,i,j,v] <= 1;
/* ============== Commit constraints ============== */

/* ============== Change view constraints ============== */
sendCVOnlyOncePerView{i in R, v in V}: sum{t in T} SendCV[t,i,v] <= 1;
receivedCVSS{t in T, i in R, v in V: t>1}: RecvCV[t,i,i,v] = SendCV[t,i,v];
receivedCV{t in T, i in R, j in R, v in V: t>1 and j!=i}: RecvCV[t,i,j,v] <= sum{t2 in T: t2<t and t2>1} SendCV[t2,j,v];
receivedCVOnlyOnce{i in R, j in R, v in V}: sum{t in T} RecvCV[t,i,j,v] <= 1;
/* ============== Change view constraints finished ============== */

/* ============== Block relay constraints ============== */
blockRelayOptionallyOnlyIfEnoughCommits{t in T, i in R, v in V: t>1}: BlockRelay[t, i, v] <= (sum{t2 in T: t2<=t} sum{j in R} RecvCommit[t2,i,j,v])/M;
blockRelayOnlyOncePerView{i in R, v in V}: sum{t in T} BlockRelay[t,i,v] <= 1;
/* ============== Block relay constraints finished ============== */

/* ============== HONEST NODES CONSTRAINTS ==============*/
/* ----- Force nodes to receive if comes from Honest --- */
/* We assume that messages will arrive within the simulation limits for NonByz*/
#prepReqReceivedNonByz {i in R_OK, j in R_OK, v in V: j!=i}: sum{t in T: t>1} RecvPrepReq[t,i,j,v]  >= sum{t in T: t>1} SendPrepReq[t,j,v];
#prepRespReceivedNonByz{i in R_OK, j in R_OK, v in V: j!=i}: sum{t in T: t>1} RecvPrepResp[t,i,j,v] >= sum{t in T: t>1} SendPrepRes[t,j,v];
#commitReceivedNonByz  {i in R_OK, j in R_OK, v in V: j!=i}: sum{t in T: t>1} RecvCommit[t,i,j,v]   >= sum{t in T: t>1} SendCommit[t,j,v];
# AT LEAST ONLY CV should be received - THE OTHER 3 ABOVE SHOULD NOT BE ENFORCED
cvReceivedNonByz      {i in R_OK, j in R_OK, v in V: j!=i}: sum{t in T: t>1} RecvCV[t,i,j,v]       >= sum{t in T: t>1} SendCV[t,j,v];
/* ----- Force nodes to receive if comes from Honest --- */

# 2 acts as a BIGNUM
# to force a Primary to exist if any honest knows change views
assertAtLeastOnePrimaryIfEnoughCV{i in R_OK, v in V: v>1}: (sum{ii in R} Primary[ii,v])*2    >= (changeViewRecvPerNodeAndView[i,v-1] - M + 1);

/* We assume that honest nodes will perform an action within the simulation limits*/
assertSendPrepReqWithinSimLimit  {i in R_OK, v in V}: sum{t in T: t>1}  SendPrepReq[t,i,v]   >= Primary[i,v];
assertSendPrepResWithinSimLimit  {i in R_OK, v in V}: sum{t in T: t>1}  SendPrepRes[t,i,v]   >= sum{t in T: t>1} sum{j in R} RecvPrepReq[t,i,j,v];
assertSendCommitWithinSimLimit   {i in R_OK, v in V}: (sum{t in T: t>1} SendCommit[t,i,v])*2 >= ((sum{t in T: t>1} sum{j in R} RecvPrepResp[t,i,j,v]) - M + 1);
assertBlockRelayWithinSimLimit   {i in R_OK, v in V}: (sum{t in T: t>1} BlockRelay[t,i,v])*2 >= ((sum{t in T: t>1} sum{j in R} RecvCommit[t,i,j,v]) - M + 1);

/* We assume that honest nodes will only perform an action if view change was approved - no view jumps 
- not tested if really needed */
sendPrepResOnlyIfViewBeforeOk    {i in R_OK, v in V: v>1}: sum{t in T: t>1} SendPrepRes[t,i,v] <= changeViewRecvPerNodeAndView[i,v-1]/M;
sendPrepReqOnlyIfViewBeforeOk    {i in R_OK, v in V: v>1}: sum{t in T: t>1} SendPrepReq[t,i,v] <= changeViewRecvPerNodeAndView[i,v-1]/M;
sendCommitOnlyIfViewBeforeOk     {i in R_OK, v in V: v>1}: sum{t in T: t>1} SendCommit[t,i,v]  <= changeViewRecvPerNodeAndView[i,v-1]/M;
sendCVNextViewOnlyIfViewBeforeOk {i in R_OK, v in V: v>1}: sum{t in T: t>1} SendCV[t,i,v]      <= changeViewRecvPerNodeAndView[i,v-1]/M;

# Send CV if not ReceivedPrepReq
assertSendCVIfNotRecvPrepReqV1{i in R_OK}:   sum{t in T: t>1} SendCV[t,i,1]   >= (1 - (sum{j in R} sum{t in T: t>1} RecvPrepReq[t,i,j,1]));
assertSendCVIfNotEnoughPrepResV1{i in R_OK}: sum{t in T: t>1} SendCV[t,i,1]*2 >= (M - sum{j in R} sum{t in T: t>1} RecvPrepResp[t,i,j,1]);
assertSendCVIfNotEnoughCommitsV1{i in R_OK}: sum{t in T: t>1} SendCV[t,i,1]*2 >= (M - sum{j in R} sum{t in T: t>1} RecvCommit[t,i,j,1]);
assertSendCVWithCommitAndPrimary{i in R_OK, v in V: v>1}: sum{t in T: t>1} SendCV[t,i,v] >= 1 - sum{j in R} sum{t in T: t>1} RecvPrepReq[t,i,j,v] - (sum{t in T: t>1} SendCommit[t, i,v-1]) - (1 - sum{ii in R} Primary[ii,v-1]);

#assertSendCVIfNotRecvPrepReq  {i in R_OK, v in V: v>1}: sum{t in T} SendCV[t,i,v] >= (1 - (sum{j in R} sum{t in T} RecvPrepReq[t,i,j,v])) - (1 - sum{ii in R} Primary[ii,v-1]) - ; 
# Mayber other asserts should be included here

/* HONEST NODES CONSTRAINTS */
# Even non byzantine. However, it was interesting observed that it could happen if R_OK on blockRelayLimitToOneForNonByz
blockRelayLimitToOneForNonByz{i in R_OK}: sum{t in T} sum{v in V} BlockRelay[t,i,v] <= 1;

/* LINKS CV AND PrepReq,PrepRes and Commit */
noPrepReqIfCV    {i in R_OK, v in V, t in T: t>1}: SendPrepReq[t,i,v] <= 1 - sum{t2 in T: t2<=t and t2>1} SendCV[t2,i,v];
noPrepResIfCV    {i in R_OK, v in V, t in T: t>1}: SendPrepRes[t,i,v] <= 1 - sum{t2 in T: t2<=t and t2>1} SendCV[t2,i,v];
noCommitIfCV     {i in R_OK, v in V, t in T: t>1}: SendCommit[t,i,v]  <= 1 - sum{t2 in T: t2<=t and t2>1} SendCV[t2,i,v];
/* LINKS Commit and LIMITS - analogous as the constrains for SendCV*/
noCVIfCommit     {i in R_OK, v in V, t in T: t>1}: SendCV[t,i,v]      <= 1 - sum{t2 in T: t2<=t and t2>1} SendCommit[t2,i,v];
/* LINKS BlockRelayed and LIMITS - analogous as the constrains for SendCV */
noBlockYesCV     {i in R_OK, v in V, t in T: t>1}: SendCV[t,i,v]      <= 1 - sum{t2 in T: t2<=t and t2>1} BlockRelay[t2,i,v];
noBlockYesPrepReq{i in R_OK, v in V, t in T: t>1}: SendPrepReq[t,i,v] <= 1 - sum{t2 in T: t2<=t and t2>1} BlockRelay[t2,i,v];
noBlockYesPrepRes{i in R_OK, v in V, t in T: t>1}: SendPrepRes[t,i,v] <= 1 - sum{t2 in T: t2<=t and t2>1} BlockRelay[t2,i,v];
noBlockYesCommit {i in R_OK, v in V, t in T: t>1}: SendCommit[t,i,v]  <= 1 - sum{t2 in T: t2<=t and t2>1} BlockRelay[t2,i,v];
/* LINKS BlockRelayed and LIMITS in past views*/
noBlockOldViewsYesPrimary {i in R_OK, v in V: v>1}: Primary[i,v]                        <= 1 - sum{t in T: t>1} sum{v2 in V: v2<v} BlockRelay[t,i,v2];
noBlockOldViewsYesPrepReq {i in R_OK, v in V: v>1}: sum{t in T: t>1} SendPrepReq[t,i,v] <= 1 - sum{t in T: t>1} sum{v2 in V: v2<v} BlockRelay[t,i,v2];
noBlockOldViewsYesPrepRes {i in R_OK, v in V: v>1}: sum{t in T: t>1} SendPrepRes[t,i,v] <= 1 - sum{t in T: t>1} sum{v2 in V: v2<v} BlockRelay[t,i,v2];
noBlockOldViewsYesCommit  {i in R_OK, v in V: v>1}: sum{t in T: t>1} SendCommit[t,i,v]  <= 1 - sum{t in T: t>1} sum{v2 in V: v2<v} BlockRelay[t,i,v2];
/* LINKS Commit and LIMITS in past views*/
noCommitOldViewsYesPrepReq{i in R_OK, v in V: v>1}: sum{t in T: t>1} SendPrepReq[t,i,v] <= 1 - sum{t in T: t>1} sum{v2 in V: v2<v} SendCommit[t,i,v2];
noCommitOldViewsYesPrepRes{i in R_OK, v in V: v>1}: sum{t in T: t>1} SendPrepRes[t,i,v] <= 1 - sum{t in T: t>1} sum{v2 in V: v2<v} SendCommit[t,i,v2];
noCommitOldViewsYesCommit {i in R_OK, v in V: v>1}: sum{t in T: t>1} SendCommit[t,i,v]  <= 1 - sum{t in T: t>1} sum{v2 in V: v2<v} SendCommit[t,i,v2];
noCommitOldViewsYesCV     {i in R_OK, v in V: v>1}: sum{t in T: t>1} SendCV[t,i,v]      <= 1 - sum{t in T: t>1} sum{v2 in V: v2<v} SendCommit[t,i,v2];
/* ============== HONEST NODES CONSTRAINTS ==============*/

/* ============== Calculation of auxiliary variables ============== */
calcIfBlockRelayedOnView{v in V}: blockRelayed[v] <= sum{t in T} sum{i in R} BlockRelay[t, i, v];
calcIfBlockRelayedOnView2{v in V}: blockRelayed[v]*tMax*N >= sum{t in T} sum{i in R} BlockRelay[t, i, v];
calcSumBlockRelayed: totalBlockRelayed = sum{v in V} blockRelayed[v];
calcTotalPrimaries: numberOfRounds = sum{i in R} sum{v in V} Primary[i,v];
calcPrepReqSendEveryNodeAndView{i in R, v in V}: prepReqSendPerNodeAndView[i,v] = sum{t in T} SendPrepReq[t,i,v]*t;
calcPrepRespSendEveryNodeAndView{i in R, v in V}: prepRespSendPerNodeAndView[i,v] = sum{t in T} SendPrepRes[t,i,v]*t;
calcCommitSendEveryNodeAndView{i in R, v in V}: commitSendPerNodeAndView[i,v] = sum{t in T} SendCommit[t,i,v]*t;
calcCVSendEveryNodeAndView{i in R, v in V}: changeViewSendPerNodeAndView[i,v] = sum{t in T} SendCV[t,i,v]*t;
calcBlockRelayEveryNodeAndView{i in R, v in V}: blockRelayPerNodeAndView[i,v] = sum{t in T} BlockRelay[t,i,v]*t;
calcPrepReqEveryNodeAndView{i in R, v in V}: prepReqRecvPerNodeAndView[i,v] = (sum{j in R} sum{t in T} RecvPrepReq[t,i,j,v]*t);
calcPrepResponseEveryNodeAndView{i in R, v in V}: prepRespRecvPerNodeAndView[i,v] = (sum{j in R} sum{t in T} RecvPrepResp[t,i,j,v]);
calcCommitEveryNodeAndView{i in R, v in V}: commitRecvPerNodeAndView[i,v] = (sum{j in R} sum{t in T} RecvCommit[t,i,j,v]);
calcChangeViewEveryNodeAndView{i in R, v in V}: changeViewRecvPerNodeAndView[i,v] = (sum{j in R} sum{t in T} RecvCV[t,i,j,v]);
# Generation for maximization
calcLastRelayedBlockMaxProblem{t in T, i in R, v in V}: lastRelayedBlock >= ((v-1)*tMax*BlockRelay[t,i,v] + BlockRelay[t,i,v]*t);
/* ============== Calculation of auxiliary variables finished ============== */

/* ============== Obj Function ============== */
#minimize obj: totalBlockRelayed;
#minimize obj: totalBlockRelayed + numberOfRounds*-1*100 + (sum{i in R} aV[i]*100000) + (a+b+c)*100000;
maximize obj: totalBlockRelayed*1000 + lastRelayedBlock*-1; 
maximize obj: totalBlockRelayed*1000 + numberOfRounds; 
# lastRelayedBlock + 
# + numberOfRounds*-1
#*1000 + lastRelayedBlock;
#maximize obj: totalBlockRelayed * 100 + lastRelayedBlock +  sum{i in R} sum{v in V} changeViewRecvPerNodeAndView[i,v];
/* ============== Obj Function finished ============== */