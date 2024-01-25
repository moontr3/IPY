
class SpritesheetException(Exception):
    def __init__(self, message:str, file:str, line_number:int):
        super().__init__(message)
        self.message: str = message
        self.file_name: str = file
        self.line_number: int = line_number

class EngineException(Exception):
    def __init__(self, message:str, file:str):
        super().__init__(message)
        self.message: str = message
        self.file_name: str = file