
### objets mathematiques

case/role/int/job

lambda = var -> f(var)
set = {}
list = \[\]

prédicat trivial = case : role
predicat de présence = set\<case\> : int role
predicat d'absence = set\<case\> !: int role

axis : set\<case\>
	# s.t : forme de ligne, taille selon row/col
ax_list : list\<axis\>
	# s.t : taille selon row/col

### predicat operation

MAP(set<>, lambda) -> set\<pred\>

AND(set\<pred\>) -> p & p & ... & p

OR(set\<pred\>) -> o | o | ... | o

| = or operation
& = and operation

### set operations

$\cap$ = inter operation
$-$ = minus operation
### global operations

RANGE(min, max) -> \[ min ... max\]
	RANGE(MIN(ax_list), MAX(ax_list))	=>	\[1, 2, 3, 4, 5\]
NGH(case) -> set\<case\>
CARD(set\<case\>) -> int
POS(job) -> set\<case\>
PARITY_RANGE(parity, max) -> list\<int\>
	# "even" -> [0, 2, 4, ..., max]
	# "odd"  -> [1, 3, 5, ..., max]
DPOS(set\<case\>, dir) -> set\<case\>
	# shift l'ensemble de case vers dir

### ax_list operations

MIN(ax_list) -> int
	# indice minimum de l'ax_list (1)
MAX(ax_list) -> int
	# indice maximum de l'ax_list (4 ou 5)
	# b.size()
PICK(ax_list, nb) -> axis
	# take only the nb-ieme value of b
NBE(ax_list) -> int
	# CARD(axis)


|          | NB ...                                                               |
| -------- | -------------------------------------------------------------------- |
| [[TA_1]] | nb1=NB "of the" nb2=NB r=role pos1=pos be pos2=super_pos             |
|          | pos1 $\cap$ pos2 : nb1 r<br>&<br>pos1 : nb2 r                        |
| [[TA_2]] | nb1=nb_no r=role pos1=pos be pos2=super_pos                          |
|          | pos1 $\cap$ pos2 : nb1 r                                             |
| [[TA_3]] | nb=NB "of" name1=NAME_S nb2=NB r=role ngh "also neighbor" name2=NAME |
|          | NGH(name1) $\cap$ NGH(name2) : nb r<br>&<br>NGH(name1) : nb2 r       |
| [[TA_4]] | nb=NB of name=NAME_S ngh pos=pos be r=role                           |
|          | NGH(name) $\cap$ pos : nb r                                          |
| [[TA_5]] | nb1=NB "of the" nb2=NB r=role job=job be pos=pos                     |
|          | POS(job) $\cap$ pos : nb1 r<br>&<br>POS(job) : nb2 r                 |
| [[TA_6]] | nb1=NB r=role job=job be pos=pos                                     |
|          | POS(job) $\cap$ pos : nb1 r                                          |


|          | NAME ...                                                                      |
| -------- | ----------------------------------------------------------------------------- |
| [[TB_1]] | name=NAME is one of nb=NB r=role pos=pos                                      |
|          | name : r<br>&<br>pos : nb r                                                   |
| [[TB_2]] | name1=NAME is one of name2=NAME_S nb=NB r=role ngh                            |
|          | name1 : r<br>&<br>NGH(name2) : nb r                                           |
| [[TB_3]] | name=NAME has nb=NB r=role ngh                                                |
|          | NGH(name) : nb r                                                              |
| [[TB_4]] | name=NAME is the only person pos=pos with nb=NB r=role ngh                    |
|          | NGH(name) : nb r<br>&<br>AND(MAP(pos $-$ name, p -><br>  NGH(p) !: nb r<br>)) |
| [[TB_5]] | name=NAME is r=role                                                           |
|          | name : r                                                                      |
| [[TB_6]] | name=NAME "has" nb_no r=role ngh pos=pos                                      |
|          | NGH(name) $\cap$ pos : nb r                                                   |

|          | THERE ...                                                                                                                                                                 |
| -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [[TC_1]] | there nb=NB r=role pos=pos                                                                                                                                                |
|          | pos : nb r                                                                                                                                                                |
| [[TC_2]] | there at least nb=NB r=role pos=pos                                                                                                                                       |
|          | OR(MAP(RANGE(nb, CARD(pos)), a -> <br>    pos : a r<br>))                                                                                                                 |
| [[TC_3]] | There are more r=role in ax_list=AXIS c1=COORD than AXIS c2=COORD                                                                                                         |
|          | OR(MAP(RANGE(1, NBE(ax_list)), nb -><br>    PICK(ax_list, c1) : nb r<br>	&<br>	OR(MAP(RANGE(0, nb - 1), nb2 -> <br>	    PICK(ax_list, c2): nb2 r<br>	))<br>))             |
| [[TC_4]] | There are less r=role in ax_list=AXIS c1=COORD than AXIS c2=COORD                                                                                                         |
|          | OR(MAP(RANGE(0, NBE(ax_list) -1), nb -><br>    PICK(ax_list, c1) : nb r<br>	&<br>	OR(MAP(RANGE(nb+1, NBE(ax_list)), nb2 -> <br>	    PICK(ax_list, c2): nb2 r<br>	))<br>)) |
| [[TC_5]] | There's an equal number of r=role in ax_list=AXIS c1=COORD and c2=COORD                                                                                                   |
|          | OR(MAP(RANGE(0, NBE(ax_list)), nb -><br>    PICK(ax_list, c1): nb r <br>	&<br>	PICK(ax_list, c2): nb r<br>))                                                              |
| [[TC_6]] | there nb=NB r=role j=job                                                                                                                                                  |
|          | POS(job) : nb r                                                                                                                                                           |
| [[TC_7]] | there at least nb=NB r=role j=job                                                                                                                                         |
|          | OR(MAP(RANGE(nb, CARD(POS(job))), n -><br>  POS(job): n r<br>))                                                                                                           |


|          | MISC                                                                                                                                                                                                                   |
| -------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [[TD_1]] | Each ax_list=AXIS has at least nb=NB r=role                                                                                                                                                                            |
|          | AND(MAP(ax_list, a -> <br>    OR(MAP(RANGE(nb, NBE(ax_list)), b -> <br>	    a : b r <br>	))<br>))                                                                                                                      |
| [[TD_2]] | Only one ax_list=AXIS has nb=NB r=role                                                                                                                                                                                 |
|          | OR(MAP(ax_list, a -> <br>    a : nb r <br>	&<br>	AND(MAP(ax_list $-$ a, p -><br>	   p !: nb r<br>	))<br>))                                                                                                             |
| [[TD_3]] | ax_list=AXIS c=COORD is the only AXIS with nb=NB r=role                                                                                                                                                                |
|          | PICK(ax_list, c) : nb r<br>&<br>AND(MAP(ax_list $-$ PICK(ax_list, c), p -><br>  p !: nb r<br>))                                                                                                                        |
| [[TD_4]] | ax_list=AXIS c=COORD has more role than any other AXIS                                                                                                                                                                 |
|          | OR(MAP(RANGE(1, NBE(ax_list)), a -> <br>    PICK(ax_list, c) : a r<br>	&<br>	AND(MAP(ax_list $-$ PICK(ax_list, c), pos -> <br>	    OR(MAP(RANGE(0, a - 1), b -><br>		    pos : b r<br>		))<br>	))<br>))                |
| [[TD_5]] | ax_list=AXIS c=COORD has less role than any other AXIS                                                                                                                                                                 |
|          | OR(MAP(RANGE(0, NBE(ax_list) - 1), a -> <br>    PICK(ax_list, c) : a r<br>	&<br>	AND(MAP(ax_list $-$ PICK(ax_list, c), pos -> <br>	    OR(MAP(RANGE(a + 1, NBE(ax_list)), b -><br>		    pos : b r<br>		))<br>	))<br>)) |


|          | GLOBAL ...                                                                                                                                                     |
| -------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [[TE_1]] | There are more r1=role j1=job than r2=role j2=job                                                                                                              |
|          | OR(MAP(RANGE(1, CARD(POS(j1))), a -> <br>  POS(j1) : a r<br>  &<br>  OR(MAP(RANGE(0, min(CARD(POS(j2)), a-1)), b -><br>		POS(j2) : b r<br>	))<br>))            |
| [[TE_2]] | There are less r1=role j1=job than r2=role j2=job                                                                                                              |
|          | OR(MAP(RANGE(0, min(CARD(POS(j1)), CARD(POS(j2))), a -> <br>  POS(j1) : a r<br>  &<br>  OR(MAP(RANGE(a+1, CARD(POS(j2))), b -><br>		POS(j2) : b r<br>	))<br>)) |
| [[TE_3]] | There are as many role job as there are role job                                                                                                               |
|          | OR(MAP(RANGE(0,min(CARD(POS(j1)), CARD(POS(j2)))), n -> <br>  POS(j1) : n r<br>  &<br>  POS(j2) : n r<br>))                                                    |

|          | NEGATIV                                   |
| -------- | ----------------------------------------- |
| [[TF_1]] | "no one" pos=pos "has" a_det r=role ngh   |
|          | AND(MAP(pos, p -><br>  NGH(p) : 0 r<br>)) |

|           | TMP                                                                                                                                 |
| --------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| [[TMP2]]  | name1=NAME has nb=NB less r=role neighbor than name2=NAME                                                                           |
|           | OR(MAP(RANGE(0, min(CARD(NGH(name1)), CARD(NGH(name2))-nb)), a -> <br>    NGH(name1) : a r <br>	&<br>	NGH(name2) : (a + nb) r<br>)) |
| [[TMP3]]  | name1=NAME has nb=NB more r=role neighbor than name2=NAME                                                                           |
|           | OR(MAP(RANGE(0, min(CARD(NGH(name2)), CARD(NGH(name1))-nb)), a -> <br>    NGH(name1) : (a + nb) r <br>	&<br>	NGH(name2) : a r<br>)) |
| [[TMP4]]  | "an" PARITY "number of" role pos neighbor name=NAME                                                                                 |
|           | OR(MAP(PARITY_RANGE(parity, CARD(pos $\cap$ NGH(name))), n -> <br>    pos $\cap$ NGH(name) : n r<br>))                              |
| [[TMP5]]  | "an" PARITY "number of" role pos "are" name=NAME_S ngh                                                                              |
|           | OR(MAP(PARITY_RANGE(parity, CARD(pos $\cap$ NGH(name))), n -> <br>    pos $\cap$ NGH(name) : n r<br>))                              |
| [[TMP6]]  | there "an" PARITY "number of" role pos                                                                                              |
|           | OR(MAP(PARITY_RANGE(parity, CARD(pos)), n -> <br>    pos : n r<br>))                                                                |
| [[TMP7]]  | ALLBOTH role pos are connected                                                                                                      |
| [[TMP9]]  | name1=NAME and name2=NAME have nb=nb_no r=role ngh in common                                                                        |
|           | NGH(name1) $\cap$ NGH(name2) : nb r                                                                                                 |
| [[TMP10]] | nb1=NB "of the" nb2=NB job=job has a_det r=role "directly" dir=dir "them"                                                           |
|           | DPOS(POS(job), dir) : nb1 r                                                                                                         |
| [[TMP11]] | nb1=NB job=job has a_det r=role "directly" dir=dir "them"                                                                           |
|           | DPOS(POS(job), dir) : nb1 r                                                                                                         |
| [[TMP14]] | ALLBOTH job=job be r=role                                                                                                           |
|           | POS(job) : CARD(POS(job)) r                                                                                                         |
| [[TMP15]] | name=NAME "has at least" nb=NB r=role ngh                                                                                           |
|           | OR(MAP(RANGE(nb, CARD(NGH(name))), a -> <br>    NGH(name) : a r<br>))                                                               |
| [[TMP17]] | name1=NAME "and" name2=NAME "have an equal number of" r=role ngh                                                                    |
|           | OR(MAP(RANGE(0, min(CARD(NGH(name1)), CARD(NGH(name2)))), n -> <br>    NGH(name1) : n r<br>	&<br>	NGH(name2) : n r<br>))            |
| [[TMP18]] | nb=NB person pos=pos has a_det r=role "directly" dir=dir "them"                                                                     |
|           |                                                                                                                                     |
| [[TMP19]] | nb=NB r=role pos=pos has a_det r=role "directly" dir=dir "them"                                                                     |
|           |                                                                                                                                     |
| [[TMP20]] | name=NAME is the only on with nb=NB r=role ngh                                                                                      |
|           |                                                                                                                                     |
| [[TMP21]] | No one pos has more than NB role ngh                                                                                                |
|           |                                                                                                                                     |
| [[TMP22]] | No one pos has less than NB role ngh                                                                                                |
|           |                                                                                                                                     |

refactor DPOS de tel sorte que ça genere des predicat triviaux