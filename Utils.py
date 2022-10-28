from typing import Final
from datetime import datetime

_BUFFER_SIZE: Final[int] = 2048
_SERVER: Final[str] = "localhost"
_SERVER_PORT: Final[int] = 12000

_COMMANDS = ["hi, meu nome eh ", "bye", "list", "@", "ban"]

def time():
    return datetime.now().strftime("%H:%M:%S")