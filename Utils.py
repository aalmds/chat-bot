from typing import Final
from datetime import datetime

_BUFFER_SIZE: Final[int] = 2048
_SERVER: Final[str] = "localhost"
_SERVER_PORT: Final[int] = 12000

_CONNECT: Final[str] = "hi, meu nome eh "
_BYE: Final[str] = "bye"
_LIST: Final[str] = "list"
_INBOX: Final[str] = "@"
_BAN: Final[str] = "ban "


def time():
    return datetime.now().strftime("%H:%M:%S")