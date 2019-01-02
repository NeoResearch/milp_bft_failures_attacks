
/* consensus replica $i$ from set of replicas R */
set R;

param f; /* number of faulty/Byzantine replicas. */
param N; /* total number of replicas. $N = |R| = |R^{OK}| + |R^{BYZ}| = 3f + 1$. */
param M; /* safety level. $M = 2f + 1$. */


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
var initialized{R,H,V,T}, binary;
var SendPrepReq{R,H,B,V,T}, binary;
var SendPrepResp{R,H,B,V,T}, binary;
var RecvPrepReq{R,R,H,B,V,T}, binary;
var RecvPrepResp{R,R,H,B,V,T}, binary;
var BlockRelay{R,H,B,T}, binary;
var RecvBlkPersist{R,R,H,B,T}, binary;

var sentPrepReq{R,H,B,V,T}, binary;
var sentPrepResp{R,H,B,V,T}, binary;
var recvdPrepReq{R,R,H,B,V,T}, binary;
var recvdPrepResp{R,R,H,B,V,T}, binary;
var recvdBlkPersis{R,R,H,B,T}, binary;

var blockRelayed{B}, binary;
/* DECISION VARIABLES} */
/* ================== */

s.t. 


calcSumBlockRelayed: totalBlockRelayed = sum{b in B} blockRelayed[b];

maximize obj: totalBlockRelayed
