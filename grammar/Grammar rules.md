
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
|          | pos1 $\cap$ pos2 : nb1 r<br>pos1 : nb2 r                               |
| [[TA_2]] | nb1=nb_no r=role pos1=pos be pos2=super_pos                            |
|          | pos1 $\cap$ pos2 : nb1 r                                               |
| [[TA_3]] | nb=NB of name1=NAME_S nb2=NB r=role neighbors also neighbor name2=NAME |
|          | NGH(name1) $\cap$ NGH(name2) : nb r                                    |
| [[TA_4]] | nb=NB of name=NAME_S ngh pos=pos be r=role                             |
|          | NGH(name) $\cap$ pos : nb r                                            |

|          | NAME ...                                                   |
| -------- | ---------------------------------------------------------- |
| [[TB_1]] | name=NAME is one of nb=NB r=role pos=pos                   |
|          | name : r<br>pos : nb r                                     |
| [[TB_2]] | name1=NAME is one of name2=NAME_S nb=NB r=role ngh         |
|          | name1 : r<br>NGH(name2) : nb r                             |
| [[TB_3]] | name=NAME has nb=NB r=role ngh                             |
|          | NGH(name) : nb r                                           |
| [[TB_4]] | name=NAME is the only person pos=pos with nb=NB r=role ngh |
|          | NGH(name) : nb r<br>NGH(pos $-$ name) : NOT(nb r)          |

|          | THERE ...                                      |
| -------- | ---------------------------------------------- |
| [[TC_1]] | there nb=NB r=role pos=pos                     |
|          | pos : nb r                                     |
| [[TC_2]] | there at least nb=NB r=role pos=pos            |
|          | OR(MAP(RANGE(nb, CARD(pos)), a -> pos : a r))) |

|          | MISC                                                                                                                                                                                                                                               |
| -------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [[TD_1]] | Each axis=AXIS has at least nb=NB r=role                                                                                                                                                                                                           |
|          | ALL(axis, a -> OR(MAP(RANGE(nb, CARD(axis)), b -> PICK(axis, a) : b r )))                                                                                                                                                                          |
| [[TD_2]] | Only one axis=AXIS has nb=NB r=role                                                                                                                                                                                                                |
|          | ANY(axis, a -> PICK(axis, a) : nb r & SET(axis) - a !: nb r)                                                                                                                                                                                       |
| [[TD_3]] | axis=AXIS c=COORD is the only AXIS with nb=NB r=role                                                                                                                                                                                               |
|          | PICK(axis, c) : nb r<br>SET(axis) - c !: nb r                                                                                                                                                                                                      |
| [[TD_4]] | axis=AXIS c=COORD has COMP role than any other AXIS                                                                                                                                                                                                |
|          | OR(MAP(RANGE(1, CARD(AXIS))<br>                  a -> PICK(axis, c) : ar<br>				          & AND(MAP(SET(axis) - c,<br>						                            X -> OR(MAP(RANGE(0, a - 1),<br>													                           b -> X : b r)))))) |

|           | TMP                                                                                                                                                                                |
| --------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [[TMP1]]  | There are COMP r=role in axis=AXIS c1=COORD than AXIS c2=COORD                                                                                                                     |
|           | OR(MAP(RANGE(1, CARD(axis)),<br>                  a -> PICK(axis, c) : a r<br>				          & OR(MAP(RANGE(0, a - 1)),<br>						                        b -> PICK(axis, c2): br))) |
| [[TMP2]]  | There's an equal number of role in AXIS COORD and COORD                                                                                                                            |
|           | OR(MAP(RANGE(0, CARD(Axis)),<br>                   a -> PICK(axis, c1): a r & PICK(axis, c2): ar))                                                                                 |
| [[TMP3]]  | name1=NAME has nb=NB COMP r=role neighbor than name2=NAME                                                                                                                          |
|           | OR(MAP(RANGE(0, CARD(NGH) - nb),<br>                  a -> name1 : a + nb : r & name2 : nb r))                                                                                     |
| [[TMP4]]  | parity_count neighbor NAME                                                                                                                                                         |
| [[TMP5]]  | parity_count are NAME_S ngh                                                                                                                                                        |
| [[TMP6]]  | there parity_count                                                                                                                                                                 |
| [[TMP7]]  | ALLBOTH role pos are connected                                                                                                                                                     |
| [[TMP9]]  | NAME and NAME have nb_no role ngh in common                                                                                                                                        |
| [[TMP10]] | nb_with_opt_filter job has a_det role directly dir them                                                                                                                            |
| [[TMP12]] | There are COMP role job than role job                                                                                                                                              |
| [[TMP13]] | There are as many role job as there are role job                                                                                                                                   |
| [[TMP14]] | ALLBOTH job be role                                                                                                                                                                |
| [[TMP15]] | NAME "has at least" NB role ngh                                                                                                                                                    |
| [[TMP16]] | NB "of" NAME_S NB role ngh "also neighbor" NAME                                                                                                                                    |

### NO MATCH
