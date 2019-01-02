# A MILP Model for Failures and Attacks on a BFT Blockchain Protocol


We present a MIP model for failures and attacks on a BFT blockchain protocol.

** Parameters **

* \item  [{$i \in R$}:] consensus replica $i$ from set of replicas $R$. $R^{BYZ}$ is byzantine set. $R^{OK}$ is non-byzantine set. $R = R^{OK} \cup R^{BYZ}$, such that $R^{OK} \cap R^{BYZ} = \emptyset$.
* \item  [$f$:] number of faulty/Byzantine replicas. $f = |R^{BYZ}|$.
* \item  [$N$:] total number of replicas. $N = |R| = |R^{OK}| + |R^{BYZ}| = 3f + 1$.
* \item  [$M$:] safety level. $M = 2f + 1$.
* \item  [{$b \in B$}:] block $b$ from set of possible proposed blocks $B$ (may be understood as block hash).  $B = \{b_0, b_1, b_2, \cdots \}$.
*  \item  [{$h \in H$}:] height $h$ from set of possible heights $H$ (tests may only require two or three heights). $H = \{h_0, h_1, h_2\}$.
* \item  [{$v \in V$}:] view $v$ from set of possible views $V$ (number of views may be limited to the number of consensus nodes $N$). $V = \{v_0, v_1, \cdots , v_{N-1}\}$
* \item  [{$t \in T$}:] time unit $t$ from set of discrete time units $T$.  $T = \{t_0, t_1, t_2,  \cdots \}$.
