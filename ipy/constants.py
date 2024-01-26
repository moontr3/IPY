from typing import *

FORBIDDEN_KEYWORD_CHARACTERS: str = '"\'=,.$*#'

ANY = None
NULL = 0
BOOL = 1
INTEGER = 2
FLOAT = 3
STRING = 4

TYPES = {
    'ANY': ANY,
    'NULL': NULL,
    'BOOL': BOOL,
    'INTEGER': INTEGER,
    'FLOAT': FLOAT,
    'STRING': STRING
}

LIST_TYPES = [
    'NULL',
    'BOOL',
    'INTEGER',
    'FLOAT',
    'STRING'
]