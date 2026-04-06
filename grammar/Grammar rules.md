
### objets mathematique

predicat de présence = position : population
predicat d'absence = position !: population
	position = ensemble de cases
	population = nombres de roles
lambda = var -> f(var)
list = \[ \]
### predicat operation

(min, max) => RANGE => \[ min ... max\]
	(MIN(axis), MAX(axis))	=> RANGE =>	\[1, 2, 3, 4, 5\]

(list, lambda) => MAP => \[ res, res, ..., res \] 

list(objet) => AND => combinaison_objet
	\[o, o, ..., o\] => AND => o & o & ... & o

list(objet) => OR => combinaison_objet
	\[o, o, ..., o\] => OR => o | o | ... | o
| = or operation
& = and operation

### shared operation

NOT(position) => inverse de la position
NOT(population) => predicat d'absence
### position operation

$\cap$ = inter operation
$-$ = minus operation
### type operation

MIN(type) => min value
MAX(type) => max value
CARD(type) => nb values
SET(type) => all values
PICK(type, a) => take only the a-ieme value

### alias

ALL(type, lambda) = AND(MAP(RANGE(MIN(type), MAX(type)), lambda))
ANY(type, lambda) = OR(MAP(RANGE(MIN(type), MAX(type)), lambda))


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

|          | NAME ...                                                   |
| -------- | ---------------------------------------------------------- |
| [[TB_1]] | name=NAME is one of nb=NB r=role pos=pos                   |
|          | name : r<br>&<br>pos : nb r                                |
| [[TB_2]] | name1=NAME is one of name2=NAME_S nb=NB r=role ngh         |
|          | name1 : r<br>&<br>NGH(name2) : nb r                        |
| [[TB_3]] | name=NAME has nb=NB r=role ngh                             |
|          | NGH(name) : nb r                                           |
| [[TB_4]] | name=NAME is the only person pos=pos with nb=NB r=role ngh |
|          | NGH(name) : nb r<br>&<br>NGH(pos $-$ name) : NOT(nb r)     |

|          | THERE ...                                                                                                                                                    |
| -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| [[TC_1]] | there nb=NB r=role pos=pos                                                                                                                                   |
|          | pos : nb r                                                                                                                                                   |
| [[TC_2]] | there at least nb=NB r=role pos=pos                                                                                                                          |
|          | OR(MAP(RANGE(nb, CARD(pos)), a -> <br>    pos : a r<br>))                                                                                                    |
| [[TC_3]] | There are more r=role in axis=AXIS c1=COORD than AXIS c2=COORD                                                                                               |
|          | OR(MAP(RANGE(1, CARD(axis)), nb -><br>    PICK(axis, c1) : nb r<br>	&<br>	OR(MAP(RANGE(0, nb - 1), nb2 -> <br>	    PICK(axis, c2): nb2 r<br>	))<br>))        |
| [[TC_4]] | There are less r=role in axis=AXIS c1=COORD than AXIS c2=COORD                                                                                               |
|          | OR(MAP(RANGE(1, CARD(axis)), nb -><br>    PICK(axis, c1) : nb r<br>	&<br>	OR(MAP(RANGE(nb+1, CARD(axis)), nb2 -> <br>	    PICK(axis, c2): nb2 r<br>	))<br>)) |
| [[TC_5]] | There's an equal number of r=role in AXIS c1=COORD and c2=COORD                                                                                              |
|          | OR(MAP(RANGE(0, CARD(Axis)), nb -><br>    PICK(axis, c1): nb r <br>	&<br>	PICK(axis, c2): nb r<br>))                                                         |


|          | MISC                                                                                                                                                                                        |
| -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [[TD_1]] | Each axis=AXIS has at least nb=NB r=role                                                                                                                                                    |
|          | ALL(axis, a -> <br>    OR(MAP(RANGE(nb, CARD(axis)), b -> <br>	    PICK(axis, a) : b r <br>	))<br>)                                                                                         |
| [[TD_2]] | Only one axis=AXIS has nb=NB r=role                                                                                                                                                         |
|          | ANY(axis, a -> <br>    PICK(axis, a) : nb r <br>	& <br>	SET(axis) - a !: nb r<br>)                                                                                                          |
| [[TD_3]] | axis=AXIS c=COORD is the only AXIS with nb=NB r=role                                                                                                                                        |
|          | PICK(axis, c) : nb r<br>&<br>SET(axis) - c !: nb r                                                                                                                                          |
| [[TD_4]] | axis=AXIS c=COORD has more role than any other AXIS                                                                                                                                         |
|          | OR(MAP(RANGE(1, CARD(AXIS)) a -> <br>    PICK(axis, c) : a r<br>	&<br>	AND(MAP(SET(axis) - c, X -> <br>	    OR(MAP(RANGE(0, a - 1), b -><br>		    X : b r<br>		))<br>	))<br>))              |
| [[TD_5]] | axis=AXIS c=COORD has less role than any other AXIS                                                                                                                                         |
|          | OR(MAP(RANGE(1, CARD(axis)) a -> <br>    PICK(axis, c) : a r<br>	&<br>	AND(MAP(SET(axis) - c, pos -> <br>	    OR(MAP(RANGE(a + 1, CARD(axis)), b -><br>		    pos : b r<br>		))<br>	))<br>)) |


|          | GLOBAL ...                                        |
| -------- | ------------------------------------------------- |
| [[TE_1]] | There are more r1=role j1=job than r2=role j2=job |
| [[TE_2]] | There are more r1=role j1=job than r2=role j2=job |
| [[TE_3]] | There are as many role job as there are role job  |



|           | TMP                                                                                            |
| --------- | ---------------------------------------------------------------------------------------------- |
| [[TMP3]]  | name1=NAME has nb=NB more r=role neighbor than name2=NAME                                      |
| [[TMP2]]  | name1=NAME has nb=NB less r=role neighbor than name2=NAME                                      |
|           | OR(MAP(RANGE(0, CARD(NGH) - nb), a -> <br>    name1 : (a + nb) r <br>	&<br>	name2 : nb r<br>)) |
| [[TMP4]]  | parity_count neighbor NAME                                                                     |
| [[TMP5]]  | parity_count are NAME_S ngh                                                                    |
| [[TMP6]]  | there parity_count                                                                             |
| [[TMP7]]  | ALLBOTH role pos are connected                                                                 |
| [[TMP9]]  | NAME and NAME have nb_no role ngh in common                                                    |
| [[TMP10]] | nb_with_opt_filter job has a_det role directly dir them                                        |
| [[TMP14]] | ALLBOTH job be role                                                                            |
| [[TMP15]] | NAME "has at least" NB role ngh                                                                |
| [[TMP16]] | NB "of" NAME_S NB role ngh "also neighbor" NAME                                                |

### NO MATCH
