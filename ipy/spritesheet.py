from typing import *
from .errors import SpritesheetException
import pygame as pg
import numpy as np


class IPYS:
    def __init__(self, code:str, filename:str):
        '''
        IPY Spritesheet
        '''
        self.filename: str = filename # filename
        self.code: str = code # original source code
        self.blank: Tuple[int, int, int] = None

        self.palette: Dict[str, Tuple[int, int, int]]\
            = self.process_palette(code) # dictionary of RGB colors in tuples
        self.sprites: Dict[str, List[List[Tuple[int, int, int]]]]\
            = self.process_sprites(code) # dictionary of matrixes containing RGB colors in tuples
        self.surfaces: Dict[str, pg.Surface]\
            = self.process_surfaces() # dictionary of pygame surfaces

    def process_palette(self, code:str) -> Dict[str, Tuple[int, int, int]]:
        '''
        Converts source code to palette containing in code.
        '''
        # getting all palette commands
        lines: List[str] = code.split('\n')
        commands: List[Tuple[int, str]] = [] # list of lines containing palette commands
                                             # (int is the line number of the line)

        for line_num, i in enumerate(lines):
            if i.upper().startswith('=PALETTE '):
                commands.append((line_num, i[9:]))
            if i.upper().startswith('=BLANK '):
                if len(i.split(' ')) != 4:
                    raise SpritesheetException(
                        f'BLANK must contain exactly 3 values',
                        self.filename, line_num
                    )
                if False in [
                    color.isdigit() and int(color) >= 0 and int(color) <= 255\
                    for color in i.split(' ')[1:]
                ]:
                    raise SpritesheetException(
                        f'Blank colors must be valid integers from 0 to 255',
                        self.filename, line_num
                    )
                self.blank: Tuple[int, int, int] = ([int(i) for i in i.split(' ')[1:]])

        # converting commands to dict of colors
        palette: Dict[str, Tuple[int, int, int]] = {}

        for i in commands:
            command = i[1].split(' ')
            line_num = i[0]

            # error catching
            if len(command) != 4:
                raise SpritesheetException(
                    f'PALETTE must contain exactly 4 values',
                    self.filename, line_num
                )
            if len(command[0]) > 1:
                raise SpritesheetException(
                    f'Palette index must be a single character',
                    self.filename, line_num
                )
            if False in [
                color.isdigit() and int(color) >= 0 and int(color) <= 255\
                for color in command[1:]
            ]:
                raise SpritesheetException(
                    f'All palette colors must be valid integers from 0 to 255',
                    self.filename, line_num
                )
            
            # converting
            palette[command[0]] = tuple([int(color) for color in command[1:]])

        return palette


    def process_sprites(self, code:str) -> Dict[str, List[List[Tuple[int, int, int]]]]:
        '''
        Converts source code to sprites and returns them.
        '''
        # getting all image commands
        lines: List[str] = code.split('\n')
        commands: List[Tuple[int, str]] = [] # list of lines containing palette commands
                                             # (int is the line number of the line)
        
        for line_num, i in enumerate(lines):
            if i.upper().startswith('=IMAGE '):
                commands.append((line_num, i[7:]))

        # getting image data
        images: Dict[str, List[List[str]]] = {}
        for i in commands:
            command = i[1].split(' ')
            line_num = i[0]
            image_name: str = command[0]

            # catching size error
            if False in [
                number.isdigit() and int(number) > 0\
                for number in command[1:]
            ]:
                raise SpritesheetException(
                    f'All image sizes must be valid integers greater than 0',
                    self.filename, line_num
                )
            image_size: Tuple[int,int] = [int(number) for number in command[1:]]

            # getting image data
            image_data: List[str] = code.split('\n')[line_num+1:line_num+image_size[1]+1]
            if False in [len(i) == image_size[0] for i in image_data]:
                raise SpritesheetException(
                    f'Image X size not uniform or the defined X size is different than actual X size',
                    self.filename, line_num
                )
            
            # converting image to colors
            colors: List[List[Tuple(int,int,int)]] = []
            for i in image_data:
                row = []
                for colorindex in i:
                    # unknown color
                    if colorindex not in self.palette:
                        raise SpritesheetException(
                            f'Color index {colorindex} not found in palette',
                            self.filename, line_num
                        )
                    # adding color to row
                    row.append(self.palette[colorindex])
                colors.append(row)
                
            images[image_name] = colors

        return images
    

    def process_surfaces(self) -> Dict[str, pg.Surface]:
        '''
        Converts self images to pygame surfaces and returns them.
        '''
        surfaces: Dict[str, pg.Surface] = {}
        for i in self.sprites:
            sprite = np.array(self.sprites[i])
            surfaces[i] = pg.surfarray.make_surface(sprite)
            # yep
            surfaces[i] = pg.transform.rotate(surfaces[i], -90)
            surfaces[i] = pg.transform.flip(surfaces[i], True, False)
            surfaces[i].set_colorkey(self.blank)
        
        return surfaces