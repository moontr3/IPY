
class BaseException(Exception):
    def __init__(self, message:str, file:str, line_number:int):
        super().__init__(message)
        self.message: str = message
        self.file_name: str = file
        self.line_number: int = line_number
        self.text: str

class SpritesheetException(BaseException):
    def __init__(self, message:str, file:str, line_number:int):
        super().__init__(message, file, line_number)
        self.text: str = 'Spritesheet Error\n'\
            f'File {file}{f", line {line_number}" if line_number != None else ""}\n'\
            f'{message}'

class EngineException(BaseException):
    def __init__(self, message:str, file:str, line_number:int=None):
        super().__init__(message, file, line_number)
        self.text: str = 'Engine Error\n'\
            f'File {file}{f", line {line_number}" if line_number != None else ""}\n'\
            f'{message}'
        