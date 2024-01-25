import numpy as np
from typing import *

def isnumber(value: str) -> bool:
    '''
    Returns True if value is a float or an int.
    '''
    try:
        value = float(value)
    except:
        return False
    return True

def isint(value: str) -> bool:
    '''
    Returns True if value is an int.
    '''
    try:
        value = int(value)
    except:
        return False
    return True

def split_args(args:str) -> List[str]:
    '''
    Splits the given string into a list of arguments.
    '''
    in_string: bool = False # if the pointer is in a string
    in_function: bool = False # if the pointer is in a function
    out: List[str] = [] # arguments to return
    current_arg: str = ''

    for char in args:
        if char == '"':
            in_string = not in_string
            current_arg += '"'
        elif char == '$':
            in_function = not in_function
            current_arg += '$'
        elif char == ' ' and not in_string and not in_function:
            out.append(current_arg)
            current_arg = ''
        else:
            current_arg += char

    out.append(current_arg)

    return out