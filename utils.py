from typing import Final
from datetime import datetime

_BUFFER_SIZE: Final[int] = 2048
_SERVER: Final[str] = "localhost"
_SERVER_PORT: Final[int] = 12000

_CONNECT: Final[str] = "hi, meu nome eh "
_BYE: Final[str] = "bye"
_LIST: Final[str] = "list"
_INBOX: Final[str] = "@"
_BAN: Final[str] = "ban @"
_DISCONNECT: Final[str] = "disconect%&%"

_BAN_CONDITION: Final[str] = 2/3
_BAN_TIMEOUT: Final[str] = 15

_BAN_COLOR: Final[str] = "%&%red"
_CONNECTION_COLOR: Final[str] = "%&%green"
_INBOX_COLOR: Final[str] = "%&%blue"

_COLORS: Final[str] = [
    "%&%cyan",
    "%&%yellow",
    "%&%magenta"
]

def current_time():
    return datetime.now().strftime("%H:%M:%S")