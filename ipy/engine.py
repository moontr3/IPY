import pygame as pg
from typing import *
import random

from .errors import *
from .spritesheet import IPYS
from .functions import *
from .constants import *

# todo math library


class ExitCode:
    def __init__(self, success:bool, message:str=''):
        self.success: bool = success
        self.message: str = message


class Variable:
    def __init__(self, name:str, type:int, value:Any):
        self.name: str = name
        self.type: int = type
        self.value: Any = value


class Instruction:
    def __init__(self, line:str, line_number:int=None):
        self.orig_line: str = line
        self.line: int = line_number
        self.orig_instruction: str = line.split(' ')[0]
        self.orig_args: str = ' '.join(line.split(' ')[1:])

        self.instruction: str = self.orig_instruction.upper()
        self.args: List[str] = split_args(self.orig_args)


class Function:
    def __init__(self, name: str, args: Dict[str,int], code:List[Instruction]):
        self.name: str = name # function name
        self.args: Dict[str,int] = args # arguments as dict with keys as names and values as types
        self.code: List[Instruction] = code # list of instructions to execute


class IPYP:
    def __init__(self, code:str, filename:str, spritesheets:List[IPYS]=[]):
        '''
        Project engine.
        '''
        self.code: str = code # project source code
        self.compiled: List[Instruction] = [] # list of all compiled instructions
        self.pre: List[Instruction] = [] # list of all instructions excluding functions and loop
        self.functions: Dict[str, Function] = {} # list of functions
        self.loop: List[Instruction] = [] # list of instructions to run every frame

        self.arrays: Dict[str, List[Variable]] = {} # all arrays
        self.spritesheets: List[IPYS] = spritesheets # list of spritesheets
        self.sprites: Dict[str, pg.Surface] = {} # dict of sprites
        self.filename: str = filename # project filename
        self.scope: Dict[str, Variable] = {} # all variables
        self.size_update_callback: Callable = None # callback when the size of the window is changed
        self.fps: int = 0 # current frame rate (unlimited by default)
        self.surface: pg.Surface = None # surface to draw things on

        self.compile(self.code)


    def compile(self, code:str):
        '''
        Compiles the given code and saves it in self
        variables.
        '''

        # stripping comments and removing newlines
        code = ''.join(i.split('=')[0] for i in code.split('\n'))
        # splitting commands
        code = [i.strip(' ') for i in code.split(';')]
        # removing empty strings
        code = [i for i in code if i != '']
        commands = [i.upper().split(' ')[0] for i in code]

        # catching errors
        if 'LOOP' not in commands:
            raise EngineException('LOOP command not found', self.filename)
        if 'ENDLOOP' not in commands:
            raise EngineException('ENDLOOP command not found', self.filename)

        self.compiled = [Instruction(line, num+1) for num, line in enumerate(code)]

        # initial commands
        index = 0
        skip: List[str] = []
        pre: List[str] = []
        while index < len(code):
            if commands[index] == 'LOOP':
                skip.append('loop')

            elif commands[index].startswith('FUNCTION'):
                skip.append('function')
                
            if skip == []:
                pre.append((code[index], index+1))

            if  commands[index] == 'ENDLOOP':
                if 'loop' not in skip:
                    raise EngineException('Unexpected ENDLOOP', self.filename, index+1)
                skip.remove('loop')

            elif commands[index] == 'ENDFUNCTION':
                if 'function' not in skip:
                    raise EngineException('Unexpected ENDFUNCTION', self.filename, index+1)
                skip.remove('function')

            if commands[index] in ['ARGS', 'ENDARGS'] and 'function' not in skip:
                raise EngineException(f'Unexpected {commands[index]}', self.filename, index+1)

            index += 1

        self.pre = [Instruction(line[0], line[1]) for line in pre]

        # loop commands
        index = 0
        isloop = False
        loop = []
        while index < len(code):
            if commands[index] == 'LOOP':
                isloop = True

            if commands[index] == 'ENDLOOP':
                isloop = False
                self.loop = [Instruction(line[0], line[1]) for line in loop]

            if isloop:
                if commands[index] != 'LOOP':
                    loop.append((code[index], index+1))
            else:
                loop = []

            index += 1

        # functions
        index = 0
        isfunction = False
        isargs = False
        function = []
        name = None
        args: Dict[str, int] = {}

        while index < len(code):
            if commands[index] == 'FUNCTION':
                isfunction = True
                if len(code[index].split(' ')) != 2:
                    raise EngineException(f'FUNCTION requires exactly 1 argument', self.filename, index+1)
                name = code[index].split(' ')[1]
                self.check_keyword(name)

            if commands[index] == 'ENDFUNCTION':
                isfunction = False
                self.functions[name] = Function(
                    name, args,
                    [Instruction(line[0], line[1]) for line in function]
                )
                name = None
                args: Dict[str, int] = {}

            if isfunction:
                if commands[index] != 'FUNCTION':
                    if commands[index] == 'ARGS':
                        isargs = True
                    if commands[index] == 'ENDARGS':
                        isargs = False

                    if not isargs:
                        if commands[index] != 'ENDARGS':
                            function.append((code[index], index+1))
                    elif commands[index] != 'ARGS':
                        arg_args = code[index].split(' ')
                        if len(arg_args) != 2:
                            raise EngineException(
                                f'Function argument definitions need exactly 2 values (name and type)',
                                self.filename, index+1
                            )
                        
                        self.check_keyword(arg_args[0])
                        if arg_args[1].upper() not in TYPES:
                            raise EngineException(f'Unknown type {arg_args[1]}', self.filename, index+1)
                        args[arg_args[0]] = TYPES[arg_args[1].upper()]
                        
            else:
                function = []

            index += 1


    def load_spritesheet(self, filename: str):
        '''
        Loads spritesheet from a file.
        '''
        try:
            with open(filename, encoding='utf-8') as f:
                spritesheet = IPYS(f.read(), filename)
                self.spritesheets.append(spritesheet)

                for i in spritesheet.surfaces:
                    self.sprites[i] = spritesheet.surfaces[i]

        except FileNotFoundError:
            raise EngineException(f"File {filename} not found in current working directory", self.filename)
        except Exception as e:
            raise EngineException(f"Could not load spritesheet: {e}", self.filename)


    def edit_window_size(self, sizex:int, sizey:int):
        '''
        Edits window size data and calls the callback.
        '''
        if sizex > sizey:
            self.ratio: Tuple[int,int] = (1, sizey/sizex)
        elif sizey > sizex:
            self.ratio: Tuple[int,int] = (sizex/sizey, 1)
        else:
            self.ratio: Tuple[int,int] = (1,1)

        self.size: Tuple[int,int] = (sizex, sizey)
        self.size_update_callback()


    def call(self, function:str, args:List[Variable]) -> Variable:
        '''
        Calls a function.
        '''
        if function not in self.functions:
            raise EngineException(f'Unknown function {function}', self.filename)
        func: Function = self.functions[function]

        if len(args) != len(func.args):
            raise EngineException(f'Function {function} requires exactly {len(func.args)} arguments', self.filename)
        
        flat_args = [(i, func.args[i]) for i in func.args]

        for index, i in enumerate(args):
            if flat_args[index][1] != ANY and flat_args[index][1] != i.type:
                raise EngineException(
                    f'Argument {flat_args[index][0]} requires type {flat_args[index][1]}, not {i.type}',
                    self.filename
                )

        [self.set_variable(f'*{i}', str(args[index].value), force=True) for index, i in enumerate(func.args)]
        variable: Variable = self.run_code(func.code)
        # cleaning up
        for i in [f'*{var}' for var in func.args]:
            if i in self.scope:
                del self.scope[i]

        return variable


    def get_variable(self, name:str, type:int=ANY) -> Any:
        '''
        Returns variable data if found. Otherwise, throws exception.
        '''
        # if no such variable
        if name not in self.scope:
            raise EngineException(f'Unknown variable {name}', self.filename)
        var = self.scope[name]
        # checking type
        if type != ANY and var.type != type:
            raise EngineException(
                f'Type {" or ".join(type)} required, but variable {name} has type {var.type}',
                self.filename
            )
        
        return var.value
    

    def check_keyword(self, text:str):
        '''
        Checks if using a keyword as an argument is fine.
        '''
        if True in [i in FORBIDDEN_KEYWORD_CHARACTERS for i in text]:
            raise EngineException(
                f'Keyword {text} must not contain any of the following characters: '\
                    +FORBIDDEN_KEYWORD_CHARACTERS,
                self.filename
            )
    

    def get_component(self, value:str, type:List[int]=ANY):
        '''
        Returns a `Variable` object from a command argument.
        '''
        # null type
        if value.upper() == NULL or value == 'NULL':
            if type != ANY and NULL not in type:
                raise EngineException(f'Type {" or ".join(type)} required, but found type null', self.filename)
            return Variable(value, NULL, None)
        
        # bool
        elif value.upper() in ['TRUE','FALSE']:
            if type != ANY and BOOL not in type:
                raise EngineException(f'Type {" or ".join(type)} required, but found type bool', self.filename)
            return Variable(value, BOOL, value.upper()=='TRUE')
        
        # integer
        elif isint(value):
            if type != ANY and INTEGER not in type:
                raise EngineException(f'Type {" or ".join(type)} required, but found type integer', self.filename)
            return Variable(value, INTEGER, int(value))
        
        # float
        elif isnumber(value):
            if type != ANY and FLOAT not in type:
                raise EngineException(f'Type {" or ".join(type)} required, but found type float', self.filename)
            return Variable(value, FLOAT, float(value))
        
        # string
        elif value.startswith('"') and value.endswith('"'):
            if type != ANY and STRING not in type:
                raise EngineException(f'Type {" or ".join(type)} required, but found type string', self.filename)
            return Variable(value, STRING, value[1:-1])
        
        # function
        elif value.startswith('$') and value.endswith('$'):
            value = value[1:-1].split(' ')
            variable: Variable = self.call(value[0], [self.get_component(i) for i in value[1:]])
            if type != ANY and variable.type not in type:
                raise EngineException(f'Type {" or ".join(type)} required, but found type {variable.type}', self.filename)
            return variable
        
        # another variable
        elif value in self.scope:
            if type != ANY and self.scope[value].type not in type:
                raise EngineException(
                    f'Type {" or ".join([LIST_TYPES[t] for t in type])} required, '\
                        f'but found type {LIST_TYPES[self.scope[value].type]}', self.filename
                )
            return self.scope[value]
        
        # error
        else:
            raise EngineException(
                f'Unknown keyword {value} or such variable does not exist',
                self.filename
            )
        

    def to_string(self, variable:Variable) -> Variable:
        '''
        Converts an expression to string.
        '''
        match variable.type:
            case 0:
                return Variable(variable.name, STRING, 'NULL')
            
            case 1:
                return Variable(variable.name, STRING, 'TRUE' if variable.value else 'FALSE')
            
            case 2|3:
                return Variable(variable.name, STRING, str(variable.value))
            
            case 4:
                return variable
            
            case _:
                return Variable(variable.name, STRING, 'NULL')
        
    
    def set_variable(self, name:str, value:str, force:bool=False):
        # checking name
        if isnumber(name):
            raise EngineException('Variable name must not be numeric', self.filename)
        
        if not force and True in [i in name for i in FORBIDDEN_KEYWORD_CHARACTERS]:
            raise EngineException(
                f'Variable name must not contain any of the following characters: '\
                    +FORBIDDEN_KEYWORD_CHARACTERS,
                self.filename
            )
        # getting value
        value = self.get_component(value)
        # adding variable
        self.scope[name] = value


    def create_array(self, name:str):
        # checking name
        if True in [i in name for i in FORBIDDEN_KEYWORD_CHARACTERS]:
            raise EngineException(
                f'Array name must not contain any of the following characters: '\
                    +FORBIDDEN_KEYWORD_CHARACTERS,
                self.filename
            )
        # creating array
        self.arrays[name]: List[Variable] = []

         
    def run_code(self, code: List[Instruction]) -> Variable:
        '''
        Runs inputted code with goto points in local scope.
        '''
        if len(code) == 0:
            return
        
        goto_indexes: Dict[str, int] = {} # dict with keys as names and values as line numbers
        index: int = 0 # current line index
        finished: bool = False
        # running code
        while not finished:
            i = code[index]
            args = i.args

            # operations
            match i.instruction:
                # noop
                case 'NOOP':
                    continue

                # if there is an unexpected LOOP or ENDLOOP command
                case 'LOOP'|'ENDLOOP'|'FUNCTION'|'ENDFUNCTION'|'ARGS'|'ENDARGS':
                    raise EngineException(f'Unexpected {i.instruction} command', self.filename, i.line)
                
                # printing in console
                case 'LOG':
                    string: str = " ".join([str(self.get_component(var).value) for var in args])
                    print(string)

                # finish execution of current block
                case 'BREAK':
                    finished = True
                    break

                # returning value
                case 'RETURN':
                    if len(args) != 1:
                        raise EngineException(f'RETURN requires exactly 1 argument', self.filename, i.line)
                    finished = True
                    return self.get_component(args[0])

                # create goto point
                case 'POINT':
                    if len(args) != 1:
                        raise EngineException(f'POINT requires exactly 1 argument', self.filename, i.line)
                    self.check_keyword(args[0])
                    goto_indexes[args[0]] = int(index)

                # goto command
                case 'GOTO':
                    if len(args) != 1:
                        raise EngineException(f'GOTO requires exactly 1 argument', self.filename, i.line)
                    if args[0] not in goto_indexes:
                        raise EngineException(f'Unknown GOTO point: {args[0]}', self.filename, i.line)
                    index = goto_indexes[args[0]]
                    continue

                # function calling
                case 'CALL':
                    if len(args) < 1:
                        raise EngineException(f'CALL requires at least 1 argument', self.filename, i.line)
                    self.check_keyword(args[0])
                    self.call(args[0], [self.get_component(arg) for arg in args[1:]])

                
                # variable management

                # assign a value to a global variable
                case 'ASSIGN':
                    if len(args) != 2:
                        raise EngineException(f'ASSIGN requires exactly 2 arguments', self.filename, i.line)
                    self.check_keyword(args[0])
                    self.set_variable(args[0], args[1])


                # arrays

                # create a new array
                case 'ARRAY':
                    if len(args) != 1:
                        raise EngineException(f'ASSIGN requires exactly 1 argument', self.filename, i.line)
                    self.check_keyword(args[0])
                    self.create_array(args[0])

                # append an element to the end of the array
                case 'APPEND':
                    if len(args) != 2:
                        raise EngineException(f'APPEND requires exactly 2 arguments', self.filename, i.line)
                    
                    self.check_keyword(args[0])
                    if args[0] not in self.arrays:
                        raise EngineException(f'Unknown array {args[0]}', self.filename, i.line)
                    var = self.get_component(args[1])
                    self.arrays[args[0]].append(var)

                # remove an element from the array by index
                case 'REMOVE':
                    if len(args) != 2:
                        raise EngineException(f'REMOVE requires exactly 2 arguments', self.filename, i.line)
                    
                    self.check_keyword(args[0])
                    if args[0] not in self.arrays:
                        raise EngineException(f'Unknown array {args[0]}', self.filename, i.line)
                    
                    ind = self.get_component(args[1], [INTEGER]).value
                    if ind >= len(self.arrays[args[0]]) or ind < 0:
                        raise EngineException(
                            f'Index {ind} in array {args[0]} out of bounds', self.filename, i.line
                        )
                    self.arrays[args[0]].pop(ind)

                # create a new array
                case 'LENGTH':
                    if len(args) != 2:
                        raise EngineException(f'LENGTH requires exactly 2 arguments', self.filename, i.line)
                    self.check_keyword(args[0])
                    self.check_keyword(args[1])
                    if args[0] not in self.arrays:
                        raise EngineException(f'Unknown array {args[0]}', self.filename, i.line)
                    self.set_variable(args[1], str(len(self.arrays[args[0]])))

                # create a new array
                case 'SPLIT':
                    if len(args) != 2:
                        raise EngineException(f'SPLIT requires exactly 2 arguments', self.filename, i.line)
                    string = self.get_component(args[0], [STRING]).value
                    self.check_keyword(args[1])
                    self.arrays[args[1]] = [Variable(str(ind), STRING, i) for ind, i in enumerate(list(string))]

                # write the element from the array to a variable
                case 'INDEX':
                    if len(args) != 3:
                        raise EngineException(f'INDEX requires exactly 3 arguments', self.filename, i.line)
                    
                    if args[0] not in self.arrays:
                        raise EngineException(f'Unknown array {args[0]}', self.filename, i.line)
                    ind = self.get_component(args[1], [INTEGER]).value
                    self.check_keyword(args[2])
                    
                    if ind >= len(self.arrays[args[0]]) or ind < 0:
                        raise EngineException(
                            f'Index {ind} in array {args[0]} out of bounds', self.filename, i.line
                        )
                    
                    self.scope[args[2]] = self.arrays[args[0]][ind]


                # math

                # add a value to a variable
                case 'ADD':
                    if len(args) != 2:
                        raise EngineException(f'ADD requires exactly 2 arguments', self.filename, i.line)
                    
                    self.check_keyword(args[0])
                    var = self.get_component(args[1], type=[INTEGER,FLOAT])
                    if args[0] not in self.scope:
                        raise EngineException(f'Unknown variable {args[0]}', self.filename, i.line)
                    
                    self.set_variable(args[0], str(self.scope[args[0]].value+var.value))

                # substract a value from a variable
                case 'SUB':
                    if len(args) != 2:
                        raise EngineException(f'SUB requires exactly 2 arguments', self.filename, i.line)
                    
                    self.check_keyword(args[0])
                    var = self.get_component(args[1], type=[INTEGER,FLOAT])
                    if args[0] not in self.scope:
                        raise EngineException(f'Unknown variable {args[0]}', self.filename, i.line)
                    
                    self.set_variable(args[0], str(self.scope[args[0]].value-var.value))

                # multiply a variable by a value
                case 'MUL':
                    if len(args) != 2:
                        raise EngineException(f'MUL requires exactly 2 arguments', self.filename, i.line)
                    
                    self.check_keyword(args[0])
                    var = self.get_component(args[1], type=[INTEGER,FLOAT])
                    if args[0] not in self.scope:
                        raise EngineException(f'Unknown variable {args[0]}', self.filename, i.line)
                    
                    self.set_variable(args[0], str(self.scope[args[0]].value*var.value))

                # divide a variable by a value
                case 'DIV':
                    if len(args) != 2:
                        raise EngineException(f'DIV requires exactly 2 arguments', self.filename, i.line)
                    
                    self.check_keyword(args[0])
                    var = self.get_component(args[1], type=[INTEGER,FLOAT])
                    if args[0] not in self.scope:
                        raise EngineException(f'Unknown variable {args[0]}', self.filename, i.line)
                
                    self.set_variable(args[0], str(self.scope[args[0]].value/var.value))

                # convert a variable to an integer
                case 'TOINT':
                    if len(args) != 1:
                        raise EngineException(f'TOINT requires exactly 1 argument', self.filename, i.line)
                    
                    self.check_keyword(args[0])
                    if args[0] not in self.scope:
                        raise EngineException(f'Unknown variable {args[0]}', self.filename, i.line)
                    if self.scope[args[0]].type not in [INTEGER,FLOAT]:
                        raise EngineException(f'TOINT requires an integer or a float', self.filename, i.line)
                
                    self.set_variable(args[0], str(int(self.scope[args[0]].value)))

                # generate a random integer in range
                case 'RNDINT':
                    if len(args) != 3:
                        raise EngineException(f'RNDINT requires exactly 3 arguments', self.filename, i.line)
                    
                    self.check_keyword(args[0])
                    btm = self.get_component(args[1], type=[INTEGER]).value
                    top = self.get_component(args[2], type=[INTEGER]).value
                    param = sorted([btm,top])
                
                    self.set_variable(args[0], str(random.randint(*param)))


                # variable management

                # invert a boolean variable
                case 'NOT':
                    if len(args) != 1:
                        raise EngineException(f'NOT requires exactly 1 argument', self.filename, i.line)
                    
                    self.check_keyword(args[0])
                    if args[0] not in self.scope:
                        raise EngineException(f'Unknown variable {args[0]}', self.filename, i.line)
                    if self.scope[args[0]].type != BOOL:
                        raise EngineException(f'NOT requires a bool variable', self.filename, i.line)

                    self.scope[args[0]].value = not self.scope[args[0]].value

                # invert a sign in a variable
                case 'INVERT':
                    if len(args) != 1:
                        raise EngineException(f'INVERT requires exactly 1 argument', self.filename, i.line)
                    
                    self.check_keyword(args[0])
                    if args[0] not in self.scope:
                        raise EngineException(f'Unknown variable {args[0]}', self.filename, i.line)
                    if self.scope[args[0]].type not in [INTEGER,FLOAT]:
                        raise EngineException(f'INVERT requires an integer or a float', self.filename, i.line)

                    self.scope[args[0]].value = -self.scope[args[0]].value

                # split a string into an array of characters
                case 'SPLIT':
                    if len(args) != 2:
                        raise EngineException(f'SPLIT requires exactly 2 arguments', self.filename, i.line)
                    string = self.get_component(args[0], [STRING]).value
                    self.check_keyword(args[1])
                    self.arrays[args[1]] = [Variable(str(ind), STRING, i) for ind, i in enumerate(list(string))]

                # convert a variable to string in place
                case 'TOSTRING':
                    if len(args) != 1:
                        raise EngineException(f'TOSTRING requires exactly 1 argument', self.filename, i.line)
                    self.check_keyword(args[0])
                    if args[0] not in self.scope:
                        raise EngineException(f'Unknown variable {args[0]}', self.filename, i.line)
                    string = self.to_string(self.scope[args[0]])
                    self.scope[args[0]] = string


                # logic
                    
                # if the variable equals to another run the next line
                case 'IFEQUALS':
                    if len(args) != 2:
                        raise EngineException(f'IFEQUALS requires exactly 2 arguments', self.filename, i.line)
                    var1 = self.get_component(args[0]).value
                    var2 = self.get_component(args[1]).value
                    
                    if not(var1 == var2):
                        index += 1
                    
                # if the variable doesn't equal to another run the next line
                case 'IFDIFF':
                    if len(args) != 2:
                        raise EngineException(f'IFDIFF requires exactly 2 arguments', self.filename, i.line)
                    var1 = self.get_component(args[0]).value
                    var2 = self.get_component(args[1]).value
                    
                    if not(var1 != var2):
                        index += 1
                    
                # if the variable is greater than another run the next line
                case 'IFGREATER':
                    if len(args) != 2:
                        raise EngineException(f'IFGREATER requires exactly 2 arguments', self.filename, i.line)
                    var1 = self.get_component(args[0], [INTEGER,FLOAT]).value
                    var2 = self.get_component(args[1], [INTEGER,FLOAT]).value
                    
                    if not(var1 > var2):
                        index += 1
                    
                # if the variable is smaller than another run the next line
                case 'IFSMALLER':
                    if len(args) != 2:
                        raise EngineException(f'IFSMALLER requires exactly 2 arguments', self.filename, i.line)
                    var1 = self.get_component(args[0], [INTEGER,FLOAT]).value
                    var2 = self.get_component(args[1], [INTEGER,FLOAT]).value
                    
                    if not(var1 < var2):
                        index += 1


                # window management

                # set window resolution
                case 'SETRES':
                    if len(args) != 2:
                        raise EngineException(f'SETRES requires exactly 2 arguments', self.filename, i.line)
                    x = self.get_component(args[0], type=[INTEGER]).value
                    y = self.get_component(args[1], type=[INTEGER]).value
                    if x <= 0 or y <= 0:
                        raise EngineException(f'Window size must be greater than 0', self.filename, i.line)
                    self.edit_window_size(x, y)

                # set window fps
                case 'SETFPS':
                    if len(args) != 1:
                        raise EngineException(f'SETRES requires exactly 1 argument', self.filename, i.line)
                    fps = self.get_component(args[0], type=[INTEGER]).value
                    if fps < 0:
                        raise EngineException(f'Target FPS must be greater than or equal to zero', self.filename, i.line)
                    self.fps = fps
                    
                # load spritesheet from a file
                case 'LOADSHEET':
                    if len(args) != 1:
                        raise EngineException(f'LOADSHEET requires exactly 1 argument', self.filename, i.line)
                    filename = self.get_component(args[0], type=[STRING]).value
                    self.load_spritesheet(filename)
                    
                # fill window with color and cover everything
                case 'FILL':
                    if len(args) != 3:
                        raise EngineException(f'FILL requires exactly 3 arguments', self.filename, i.line)
                    r = self.get_component(args[0], type=[INTEGER]).value
                    g = self.get_component(args[1], type=[INTEGER]).value
                    b = self.get_component(args[2], type=[INTEGER]).value
                    if (r < 0 or r > 255) or (g < 0 or g > 255) or (b < 0 or b > 255):
                        raise EngineException(f'Color value must be from 0 to 255', self.filename, i.line)
                    self.surface.fill((r,g,b))
                    
                # draw sprite on top of everything
                case 'DRAWSPRITE':
                    if len(args) != 3:
                        raise EngineException(f'DRAWSPRITE requires exactly 3 arguments', self.filename, i.line)
                    sprite = self.get_component(args[0], type=[STRING]).value
                    x = self.get_component(args[1], type=[INTEGER,FLOAT]).value
                    y = self.get_component(args[2], type=[INTEGER,FLOAT]).value
                    if sprite not in self.sprites:
                        raise EngineException(f'Sprite {sprite} not found', self.filename, i.line)
                    self.surface.blit(self.sprites[sprite], (x, y))

                # unknown command
                case _:
                    raise EngineException(f'Unknown command {i.instruction}', self.filename, i.line)
                
            # next command
            index += 1
            if index >= len(code):
                finished = True
                break

        return Variable('*RETURN_VALUE', NULL, None)


    def step(self):
        '''
        Runs game cycle.
        '''
        self.run_code(self.loop)


class App:
    def __init__(self, ipyp: IPYP):
        self.windowsize: Tuple[int,int] = (640,480)
        self.scalesize: Tuple[int,int] = [640,480]
        self.ipyp: IPYP = ipyp
        self.ipyp.size_update_callback = self.update_size

        self.running: bool = True
        self.window = pg.display.set_mode(self.windowsize)
        self.clock = pg.Clock()
        self.ipyp.surface = None

    def update_size(self):
        '''
        Updates the values of how the window is supposed to be
        resized.
        '''
        # calculating the size of the screen
        if self.windowsize[0]/self.ipyp.ratio[0] > self.windowsize[1]/self.ipyp.ratio[1]:
            self.scalesize[0] = self.windowsize[1]/self.ipyp.ratio[1]*self.ipyp.ratio[0]
            self.scalesize[1] = self.windowsize[1]

        elif self.windowsize[1]/self.ipyp.ratio[1] > self.windowsize[0]/self.ipyp.ratio[0]:
            self.scalesize[0] = self.windowsize[0]
            self.scalesize[1] = self.windowsize[0]/self.ipyp.ratio[0]*self.ipyp.ratio[1]
            
        else:
            self.scalesize[0] = self.windowsize[0]
            self.scalesize[1] = self.windowsize[1]

        # updating rect of the screen
        self.windowrect = pg.Rect((0,0),self.scalesize)
        self.windowrect.center = (self.windowsize[0]/2, self.windowsize[1]/2)
        self.window = pg.display.set_mode(self.windowsize, pg.RESIZABLE)

        # updating game surface
        self.ipyp.surface = pg.Surface(self.ipyp.size)

    def run(self):
        '''
        Runs the game loop.
        '''
        self.ipyp.run_code(self.ipyp.pre)

        while self.running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False
                if event.type == pg.VIDEORESIZE:
                    self.windowsize = (event.w, event.h)
                    self.update_size()

            self.window.fill((0,0,0))            
            self.ipyp.step()
            surface = pg.transform.scale(self.ipyp.surface, self.scalesize)
            self.window.blit(surface, self.windowrect)
            pg.display.update()
            self.clock.tick(self.ipyp.fps)
