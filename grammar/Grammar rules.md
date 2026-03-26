
### objets mathematique

predicat = position : population
	position = ensemble de cases
	population = nombres de roles
lambda = var -> f(var)
list = \[ \]

### population operation

| = or operation
& = and operation
### position operation

$\cap$ = inter operation
### predicat operation

(min, max, lambda) => RANGE => \[ res, res, ..., res\]
	(MIN(axis), MAX(axis), a -> PICK(axis, a) : nb r ) 
	=> RANGE =>
	\[ PICK(axis, 1) : nb r ,PICK(axis, 2) : nb r ,PICK(axis,3) : nb r\]

list(objet) => AND => combinaison_objet
\[o, o, ..., o\] => AND => o & o & ... & o

list(objet) => OR => combinaison_objet
\[o, o, ..., o\] => OR => o | o | ... | o

### type operation

MIN(type) => min value
MAX(type) => max value
CARD(type) => nb values
SET(type) => all values
PICK(type, a) => take only the a-ieme value

ALL(type, lambda) = AND(RANGE(MIN(type), MAX(type), lambda))
ANY(type, lambda) = OR(RANGE(MIN(type), MAX(type), lambda))
NOT(population)

|          | NB ...                                                                 |
| -------- | ---------------------------------------------------------------------- |
| [[TA_1]] | nb1=NB "of the" nb2=NB r=ROLE pos1=POS BE pos2=SUPER_POS               |
|          | pos1 $\cap$ pos2 : nb1 r<br>pos1 : nb2 r                               |
| [[TA_2]] | nb1=NB_NO r=ROLE pos1=POS BE pos2=SUPER_POS                            |
|          | pos1 $\cap$ pos2 : nb1 r                                               |
| [[TA_3]] | nb=NB of name1=NAME_S nb2=NB r=ROLE neighbors also neighbor name2=NAME |
|          | NGH(name1) $\cap$ NGH(name2) : nb r                                    |
| [[TA_4]] | NB of NAMES_S NGH POS BE ROLE                                          |
|          |                                                                        |

|          | NAME ...                                                   |
| -------- | ---------------------------------------------------------- |
| [[TB_1]] | name=NAME is one of nb=NB r=ROLE pos=POS                   |
|          | name : r<br>pos : nb r                                     |
| [[TB_2]] | name1=NAME is one of name2=NAME_S nb=NB r=ROLE neighbors   |
|          | name1 : r<br>NGH(name2) : nb r                             |
| [[TB_3]] | name=NAME has nb=NB r=ROLE NGH                             |
|          | NGH(name) : nb r                                           |
| [[TB_4]] | name=NAME is the only person pos=POS with nb=NB r=ROLE NGH |
|          | NGH(name) : nb r<br>NGH(pos $-$ name) : NOT(nb r)          |

|          | THERE ...                                 |
| -------- | ----------------------------------------- |
| [[TC_1]] | THERE nb=NB r=ROLE pos=POS                |
|          | pos : nb r                                |
| [[TC_2]] | THERE at least nb=NB r=ROLE pos=POS       |
|          | OR(RANGE(nb, CARD(pos), a -> pos : a r))) |

|          | MISC                                                                 |
| -------- | -------------------------------------------------------------------- |
| [[TD_1]] | Each axis=AXIS has at least nb=NB r=ROLE                             |
|          | ALL(axis, a -> OR(RANGE(nb, CARD(axis), b -> PICK(axis, a) : b r ))) |
| [[TD_2]] | Only one axis=AXIS has nb=NB r=ROLE                                  |
|          | ANY(axis, a -> PICK(axis, a) : nb r & SET(axis) - a : NOT(nb r))     |
| [[TD_3]] | axis=AXIS c=COORD is the only AXIS with nb=NB r=ROLE                 |
|          | PICK(axis, c) : nb r<br>SET(axis) - c : NOT(nb r)                    |


AXIS COORD has COMP ROLE than any other AXIS

There are COMP ROLE in AXIS COORD than AXIS COORD
There's an equal number of ROLE in AXIS COORD and COORD

NAME has NB COMP ROLE neighbor than NAME

An PARITY number of ROLE POS neighbor NAME
An PARITY number of ROLE POS are NAMES_S NGH
There's an PARITY number of ROLE POS

All ROLE POS are connected
Both ROLE POS are connected

NAME and NAME have NB_NO ROLE NGH in common

NB JOB has A ROLE directly to the SIDE of them
There are COMP ROLE JOB than ROLE JOB
There are as many ROLE JOB as there are ROLE JOB



