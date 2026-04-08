
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

ALL(ax_list, lambda) = AND(MAP(RANGE(MIN(ax_list), MAX(ax_list)), lambda))
ANY(ax_list, lambda) = OR(MAP(RANGE(MIN(ax_list), MAX(ax_list)), lambda))


|          | NB ...                                                                 |
| -------- | ---------------------------------------------------------------------- |
| [[TA_1]] | nb1=NB "of the" nb2=NB r=role pos1=pos be pos2=super_pos               |
|          | pos1 $\cap$ pos2 : nb1 r<br>&<br>pos1 : nb2 r                          |
| [[TA_2]] | nb1=nb_no r=role pos1=pos be pos2=super_pos                            |
|          | pos1 $\cap$ pos2 : nb1 r                                               |
| [[TA_3]] | nb=NB of name1=NAME_S nb2=NB r=role neighbors also neighbor name2=NAME |
|          | NGH(name1) $\cap$ NGH(name2) : nb r                                    |
| [[TA_4]] | nb=NB of name=NAME_S ngh pos=pos be r=role                             |
|          | NGH(name) $\cap$ pos : nb r                                            |
| [[TA_5]] | nb_with_opt_filter r=role job=job be pos=pos                           |
|          | POS(job) $\cap$ pos : nb1 r<br>&<br>POS(job) : nb2 r                   |

|          | NAME ...                                                                 |
| -------- | ------------------------------------------------------------------------ |
| [[TB_1]] | name=NAME is one of nb=NB r=role pos=pos                                 |
|          | name : r<br>&<br>pos : nb r                                              |
| [[TB_2]] | name1=NAME is one of name2=NAME_S nb=NB r=role ngh                       |
|          | name1 : r<br>&<br>NGH(name2) : nb r                                      |
| [[TB_3]] | name=NAME has nb=NB r=role ngh                                           |
|          | NGH(name) : nb r                                                         |
| [[TB_4]] | name=NAME is the only person pos=pos with nb=NB r=role ngh               |
|          | NGH(name) : nb r<br>&<br>MAP(pos $-$ name, p -><br>  NGH(p) != nb r<br>) |
| [[TB_5]] | name=NAME is r=role                                                      |
|          | name :  r                                                                |
| [[TB_6]] | name=NAME "has" nb_no r=role ngh pos=pos                                 |
|          | NGH(name) $\cap$ pos : nb r                                              |

|          | THERE ...                                                                                                                                                                 |
| -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [[TC_1]] | there nb=NB r=role pos=pos                                                                                                                                                |
|          | pos : nb r                                                                                                                                                                |
| [[TC_2]] | there at least nb=NB r=role pos=pos                                                                                                                                       |
|          | OR(MAP(RANGE(nb, CARD(pos)), a -> <br>    pos : a r<br>))                                                                                                                 |
| [[TC_3]] | There are more r=role in ax_list=AXIS c1=COORD than AXIS c2=COORD                                                                                                         |
|          | OR(MAP(RANGE(1, NBE(ax_list)), nb -><br>    PICK(ax_list, c1) : nb r<br>	&<br>	OR(MAP(RANGE(0, nb - 1), nb2 -> <br>	    PICK(ax_list, c2): nb2 r<br>	))<br>))             |
| [[TC_4]] | There are less r=role in ax_list=AXIS c1=COORD than AXIS c2=COORD                                                                                                         |
|          | OR(MAP(RANGE(1, NBE(ax_list) -1), nb -><br>    PICK(ax_list, c1) : nb r<br>	&<br>	OR(MAP(RANGE(nb+1, NBE(ax_list)), nb2 -> <br>	    PICK(ax_list, c2): nb2 r<br>	))<br>)) |
| [[TC_5]] | There's an equal number of r=role in ax_list=AXIS c1=COORD and c2=COORD                                                                                                   |
|          | OR(MAP(RANGE(0, NBE(ax_list)), nb -><br>    PICK(ax_list, c1): nb r <br>	&<br>	PICK(ax_list, c2): nb r<br>))                                                              |
| [[TC_6]] | there nb=NB r=role j=job                                                                                                                                                  |
|          |                                                                                                                                                                           |
| [[TC_7]] | there at least nb=NB r=role j=job                                                                                                                                         |
|          |                                                                                                                                                                           |


|          | MISC                                                                                                                                                                                                               |
| -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| [[TD_1]] | Each ax_list=AXIS has at least nb=NB r=role                                                                                                                                                                        |
|          | ALL(ax_list, a -> <br>    OR(MAP(RANGE(nb, NBE(ax_list)), b -> <br>	    a : b r <br>	))<br>)                                                                                                                       |
| [[TD_2]] | Only one ax_list=AXIS has nb=NB r=role                                                                                                                                                                             |
|          | ANY(ax_list, a -> <br>    a : nb r <br>	&<br>	MAP(ax_list $-$ a, p -><br>	   p !: nb r<br>	)<br>)                                                                                                                  |
| [[TD_3]] | ax_list=AXIS c=COORD is the only AXIS with nb=NB r=role                                                                                                                                                            |
|          | PICK(ax_list, c) : nb r<br>&<br>MAP(ax_list $-$ PICK(ax_list, c), p -><br>  p !: nb r<br>)                                                                                                                         |
| [[TD_4]] | ax_list=AXIS c=COORD has more role than any other AXIS                                                                                                                                                             |
|          | OR(MAP(RANGE(1, NBE(ax_list)), a -> <br>    PICK(ax_list, c) : a r<br>	&<br>	AND(MAP(ax_list $-$ PICK(ax_list, c), pos -> <br>	    OR(MAP(RANGE(0, a - 1), b -><br>		    pos : b r<br>		))<br>	))<br>))            |
| [[TD_5]] | ax_list=AXIS c=COORD has less role than any other AXIS                                                                                                                                                             |
|          | OR(MAP(RANGE(1, NBE(ax_list)), a -> <br>    PICK(ax_list, c) : a r<br>	&<br>	AND(MAP(ax_list $-$ PICK(ax_list, c), pos -> <br>	    OR(MAP(RANGE(a + 1, NBE(ax_list)), b -><br>		    pos : b r<br>		))<br>	))<br>)) |


|          | GLOBAL ...                                        |
| -------- | ------------------------------------------------- |
| [[TE_1]] | There are more r1=role j1=job than r2=role j2=job |
| [[TE_2]] | There are less r1=role j1=job than r2=role j2=job |
| [[TE_3]] | There are as many role job as there are role job  |

|          | NEGATIV                                 |
| -------- | --------------------------------------- |
| [[TF_1]] | "no one" pos=pos "has" a_det r=role ngh |

|           | TMP                                                                                                                        |
| --------- | -------------------------------------------------------------------------------------------------------------------------- |
| [[TMP3]]  | name1=NAME has nb=NB more r=role neighbor than name2=NAME                                                                  |
|           | OR(MAP(RANGE(0, min(CARD(NGH(name2)), card(NGH(name1))-nb)), a -> <br>    name1 : (a + nb) r <br>	&<br>	name2 : nb r<br>)) |
| [[TMP2]]  | name1=NAME has nb=NB less r=role neighbor than name2=NAME                                                                  |
| [[TMP4]]  | parity_count neighbor NAME                                                                                                 |
| [[TMP5]]  | parity_count are NAME_S ngh                                                                                                |
| [[TMP6]]  | there parity_count                                                                                                         |
| [[TMP7]]  | ALLBOTH role pos are connected                                                                                             |
| [[TMP9]]  | NAME and NAME have nb_no role ngh in common                                                                                |
| [[TMP10]] | nb_with_opt_filter job has a_det role "directly" dir "them"                                                                |
| [[TMP14]] | ALLBOTH job be role                                                                                                        |
| [[TMP15]] | NAME "has at least" NB role ngh                                                                                            |
| [[TMP16]] | NB "of" NAME_S NB role ngh "also neighbor" NAME                                                                            |
| [[TMP17]] | name1=NAME "and" name2=NAME "have an equal number of" r=role ngh                                                           |

