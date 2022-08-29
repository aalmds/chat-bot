from typing import Final

# Definindo constantes utilizadas para comunicacao cliente-servidor.
_BUFFER_SIZE: Final[int] = 2048
_SERVER: Final[str] = "localhost"
_SERVER_PORT: Final[int] = 12000
_FILE: Final[str] = "file"
_FINISHED: Final[str] = "finished"

# Funcao que escreve em um arquivo.
def write_file_process(chunk, file):
    try:          
        print("Writing file...")      
        file.write(chunk)
    except IOError:
        print("Error in writing file.")