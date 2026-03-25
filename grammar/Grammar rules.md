
|               | PARSED                                                                 | MATHS                                    |
| ------------- | ---------------------------------------------------------------------- | ---------------------------------------- |
| [[T1.md\|T1]] | nb1=NB "of the" nb2=NB r=ROLE pos1=POS BE pos2=SUPER_POS               | pos1 $\cap$ pos2 : nb1 r<br>pos1 : nb2 r |
| [[T2.md\|T2]] | nb1=NB_NO r=ROLE pos1=POS BE pos2=SUPER_POS                            | pos1 $\cap$ pos2 : nb1 r                 |
| [[T3.md\|T3]] | nb=NB of name1=NAME_S nb2=NB r=ROLE neighbors also neighbor name2=NAME | NGH(name1) $\cap$ NGH(name2) : nb r      |
| [[T4.md\|T4]] | name=NAME is one of nb=NB r=ROLE pos=POS                               | name : r<br>pos : nb r                   |
| [[T5.md\|T5]] | name1=NAME is one of name2=NAME_S nb=NB r=ROLE neighbors               | name1 : r<br>NGH(name2) : nb r           |




NAME has NB ROLE NGH
NAME is the only person POS with NB ROLE NGH

THERE NB ROLE POS
THERE at least NB ROLE POS

Each AXIS has at least NB ROLE
Only one AXIS has NB ROLE
AXIS COORD is the only AXIS with NB ROLE
AXIS COORD has COMP ROLE than any other AXIS

There are COMP ROLE in AXIS COORD than AXIS COORD
There's an equal number of ROLE in AXIS COORD and COORD

====================

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
