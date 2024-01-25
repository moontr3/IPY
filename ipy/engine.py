import pygame as pg
from spritesheet import IPYS
from errors import *
from typing import *
from functions import *


FORBIDDEN_CHARS = '{}"\'=,.$'


class Variable:
    def __init__(self, name:str, type:str, value:Any):
        self.name: str = name
        self.type: str = type
        self.value: Any = value


class Instruction:
    def __init__(self, line:str):
        self.line: str = line
        self.orig_instruction: str = line.split(' ')[0]
        self.orig_args: str = ' '.join(line.split(' ')[1:])

        self.instruction: str = self.orig_instruction.upper()
        self.args: List[str] = split_args(self.orig_args)


class IPYP:
    def __init__(self, code:str, filename:str, spritesheets:List[IPYS]=[]):
        '''
        Project engine.
        '''
        self.code: str = code # project source code
        self.compiled: List[Instruction] = [] # list of all compiled instructions
        self.pre: List[Instruction] = [] # list of all instructions excluding functions and loop
        self.functions: Dict[str, List[Instruction]] = {} # list of functions
        self.loop: List[Instruction] = [] # list of instructions to run every frame

        self.arrays: Dict[str, list] = {} # all arrays
        self.spritesheets: List[IPYS] = spritesheets # list of spritesheets
        self.sprites: Dict[str, pg.Surface] = {} # dict of sprites
        self.filename: str = filename # project filename
        self.scope: Dict[str, Variable] = {} # all variables
        self.size_update_callback: Callable = None # callback when the size of the window is changed
        self.fps: int = 0 # current frame rate (unlimited by default)

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
        upper_code = [i.upper() for i in code]

        # catching errors
        if 'LOOP' not in upper_code:
            raise EngineException('LOOP command not found', self.filename)
        if 'ENDLOOP' not in upper_code:
            raise EngineException('ENDLOOP command not found', self.filename)

        self.compiled = [Instruction(line) for line in code]

        # initial commands
        index = 0
        skip: List[str] = []
        pre: List[str] = []
        while index < len(code):
            if upper_code[index] == 'LOOP':
                skip.append('loop')

            elif upper_code[index] == 'FUNCTION':
                skip.append('function')

            if upper_code[index] == 'ENDLOOP':
                if 'loop' not in skip:
                    raise EngineException('Unexpected ENDLOOP', self.filename)
                skip.append('loop')

            elif upper_code[index] == 'ENDFUNCTION':
                if 'function' not in skip:
                    raise EngineException('Unexpected ENDFUNCTION', self.filename)
                skip.append('function')

            if skip == []:
                pre.append(code[index])

            index += 1

        self.pre = [Instruction(i) for i in pre]

        # loop commands
        index = 0
        isloop = False
        loop = []
        while index < len(code):
            if upper_code[index] == 'LOOP':
                isloop = True

            if upper_code[index] == 'ENDLOOP':
                isloop = False
                self.loop = [Instruction(i) for i in loop]

            if isloop:
                if upper_code[index] != 'LOOP':
                    loop.append(code[index])
            else:
                loop = []

            index += 1


    def load_spritesheet(self, filename: str):
        '''
        Loads spritesheet from a file.
        '''
        try:
            with open(filename, encoding='utf-8') as f:
                spritesheet = IPYS(f.read(), filename)
                self.spritesheets.append(spritesheet)
                for i in spritesheet.sprites:
                    self.sprites[i] = spritesheet.surfaces[i]

        except FileNotFoundError:
            EngineException(f"File {filename} not found in current working directory")
        except Exception as e:
            EngineException(f"Could not load spritesheet: {e}")


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


    def get_variable(self, name:str, type:str='any') -> Any:
        '''
        Returns variable data if found. Otherwise, throws exception.
        '''
        # if no such variable
        if name not in self.scope:
            raise EngineException(f'Unknown variable {name}', self.filename)
        var = self.scope[name]
        # checking type
        if type != 'any' and var.type != type:
            raise EngineException(
                f'Type {" or ".join(type)} required, but variable {name} has type {var.type}',
                self.filename
            )
        
        return var.value
    

    def check_keyword(self, text:str):
        if True in [i in FORBIDDEN_CHARS for i in text]:
            raise EngineException(
                f'Keyword {text} must not contain any of the following characters: '\
                    +FORBIDDEN_CHARS,
                self.filename
            )
    

    def get_component(self, value:str, type:List[str]='any'):
        # null type
        if value.upper() == 'NULL':
            if type != 'any' and 'null' not in type:
                raise EngineException(f'Type {" or ".join(type)} required, but found type null', self.filename)
            return Variable(value, 'null', None)
        # bool
        elif value.upper() in ['TRUE','FALSE']:
            if type != 'any' and 'bool' not in type:
                raise EngineException(f'Type {" or ".join(type)} required, but found type bool', self.filename)
            return Variable(value, 'bool', value.upper()=='True')
        # integer
        elif isint(value):
            if type != 'any' and 'integer' not in type:
                raise EngineException(f'Type {" or ".join(type)} required, but found type integer', self.filename)
            return Variable(value, 'integer', int(value))
        # float
        elif isnumber(value):
            if type != 'any' and 'float' not in type:
                raise EngineException(f'Type {" or ".join(type)} required, but found type float', self.filename)
            return Variable(value, 'float', float(value))
        # string
        elif value.startswith('"') and value.endswith('"'):
            if type != 'any' and 'string' not in type:
                raise EngineException(f'Type {" or ".join(type)} required, but found type string', self.filename)
            return Variable(value, 'string', value[1:-1])
        # function
        elif value.startswith('$') and value.endswith('$'):
            variable: Variable = self.call(value, string=True)
            if type != 'any' and variable.type not in type:
                raise EngineException(f'Type {" or ".join(type)} required, but found type {variable.type}', self.filename)
            return variable
        # another variable
        elif value in self.scope:
            if type != 'any' and self.scope[value].type not in type:
                raise EngineException(f'Type {" or ".join(type)} required, but found type {self.scope[value].type}', self.filename)
            return self.scope[value]
        # error
        else:
            raise EngineException(
                f'Unknown keyword {value} or such variable does not exist',
                self.filename
            )
        
    
    def set_variable(self, name:str, value:str):
        # checking name
        if isnumber(name):
            raise EngineException('Variable name must not be numeric', self.filename)
        
        if True in [i in name for i in FORBIDDEN_CHARS]:
            raise EngineException(
                f'Variable name must not contain any of the following characters: '\
                    +FORBIDDEN_CHARS,
                self.filename
            )
        # getting value
        value = self.get_component(value)
        # adding variable
        self.scope[name] = value

         
    def run_code(self, code: List[Instruction], surface:pg.Surface=None):
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

            # noop
            if i.instruction == 'NOOP':
                continue

            # if there is an unexpected LOOP or ENDLOOP command
            elif i.instruction in ['LOOP', 'ENDLOOP']:
                raise EngineException('Unexpected LOOP or ENDLOOP command(-s)', self.filename)

            # finish execution of current block
            elif i.instruction == 'BREAK':
                finished = True
                break

            # create goto point
            elif i.instruction == 'POINT':
                if len(args) != 1:
                    raise EngineException(f'POINT requires exactly 1 argument', self.filename)
                self.check_keyword(args[0])
                goto_indexes[args[0]] = int(index)

            # goto command
            elif i.instruction == 'GOTO':
                if len(args) != 1:
                    raise EngineException(f'GOTO requires exactly 1 argument', self.filename)
                if args[0] not in goto_indexes:
                    raise EngineException(f'Unknown GOTO point: {args[0]}', self.filename)
                index = goto_indexes[args[0]]
                continue
        
            # todo gotos and if statements
            # todo substractions and other operations

            
            # variable management

            # assign a value to a variable
            elif i.instruction == 'ASSIGN':
                if len(args) != 2:
                    raise EngineException(f'ASSIGN requires exactly 2 arguments', self.filename)
                self.check_keyword(args[0])
                self.set_variable(args[0], args[1])


            # math

            # add a value to a variable
            elif i.instruction == 'ADD':
                if len(args) != 2:
                    raise EngineException(f'ADD requires exactly 2 arguments', self.filename)
                self.check_keyword(args[0])
                var = self.get_component(args[1], type=['integer','float'])
                if args[0] not in self.scope:
                    raise EngineException(f'Unknown variable {args[0]}', self.filename)
                
                if var.type == 'float' and self.scope[args[0]].type == 'integer':
                    self.set_variable(args[0], str(self.scope[args[0]].value+var.value))
                self.scope[args[0]].value += var.value


            # window management

            # set window resolution
            elif i.instruction == 'SETRES':
                if len(args) != 2:
                    raise EngineException(f'SETRES requires exactly 2 arguments', self.filename)
                x = self.get_component(args[0], type=['integer']).value
                y = self.get_component(args[1], type=['integer']).value
                if x <= 0 or y <= 0:
                    raise EngineException(f'Window size must be greater than 0', self.filename)
                self.edit_window_size(x, y)

            # set window fps
            elif i.instruction == 'SETFPS':
                if len(args) != 1:
                    raise EngineException(f'SETRES requires exactly 1 argument', self.filename)
                fps = self.get_component(args[0], type=['integer']).value
                if fps < 0:
                    raise EngineException(f'Target FPS must be greater than or equal to zero', self.filename)
                self.fps = fps
                
            # load spritesheet from a file
            elif i.instruction == 'LOADSHEET':
                if len(args) != 1:
                    raise EngineException(f'LOADSHEET requires exactly 1 argument', self.filename)
                filename = self.get_component(args[0], type=['string']).value
                self.load_spritesheet(filename)
                
            # fill window with color and cover everything
            elif i.instruction == 'FILL':
                if len(args) != 3:
                    raise EngineException(f'FILL requires exactly 3 arguments', self.filename)
                r = self.get_component(args[0], type=['integer']).value
                g = self.get_component(args[1], type=['integer']).value
                b = self.get_component(args[2], type=['integer']).value
                if (r < 0 or r > 255) or (g < 0 or g > 255) or (b < 0 or b > 255):
                    raise EngineException(f'Color value must be from 0 to 255', self.filename)
                surface.fill((r,g,b))
                
            # draw sprite on top of everything
            elif i.instruction == 'DRAWSPRITE':
                if len(args) != 3:
                    raise EngineException(f'DRAWSPRITE requires exactly 3 arguments', self.filename)
                sprite = self.get_component(args[0], type=['string']).value
                x = self.get_component(args[1], type=['integer','float']).value
                y = self.get_component(args[2], type=['integer','float']).value
                if sprite not in self.sprites:
                    raise EngineException(f'Sprite {sprite} not found', self.filename)
                surface.blit(self.sprites[sprite], (x, y))

            # unknown command
            else:
                raise EngineException(f'Unknown command {i.instruction}', self.filename)
            
            # next command
            index += 1
            if index >= len(code):
                finished = True
                break


    def step(self, surface:pg.Surface):
        '''
        Runs game cycle.
        '''
        self.run_code(self.loop, surface)


class App:
    def __init__(self, ipyp: IPYP):
        self.windowsize: Tuple[int,int] = (640,480)
        self.scalesize: Tuple[int,int] = [640,480]
        self.ipyp: IPYP = ipyp
        self.ipyp.size_update_callback = self.update_size

        self.running: bool = True
        self.window = pg.display.set_mode(self.windowsize)
        self.clock = pg.Clock()

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
        self.screen = pg.Surface(self.ipyp.size)
        self.window = pg.display.set_mode(self.windowsize, pg.RESIZABLE)

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
            self.ipyp.step(self.screen)
            surface = pg.transform.scale(self.screen, self.scalesize)
            self.window.blit(surface, self.windowrect)
            pg.display.update()
            self.clock.tick(self.ipyp.fps)


if __name__ == '__main__':
    with open('mygame.ipyp', encoding='utf-8') as f:
        ipyp = IPYP(f.read(),'mygame.ipyp')
    app = App(ipyp)
    app.run()