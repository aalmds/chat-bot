import socket
import os
from Utils import _SERVER, _SERVER_PORT, _BUFFER_SIZE, _FILE, _FINISHED, write_file_process

serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Funcao que inicializa os arquivos de copia no servidor, criando o diretorio 
# para armazenar os mesmos, caso nao exista.
def create_file(message):
    # Verificando se o diretorio do servidor existe.
    if not os.path.exists("./server_files"):
        os.mkdir("./server_files")
    
    # Inicializando a copia do arquivo que sera recebido do cliente.
    return open("./server_files/received" + message.decode(), 'wb')

# Funcao que gerencia o recebimento, escrita e envio de cada um dos chunks do arquivo.
def receive_send_file(file):
    # Esperando uma mensagem do cliente.
    message, clientAddress = serverSocket.recvfrom(_BUFFER_SIZE)
    
    while message:
        # Verificando se o cliente envio um comando referente ao termino do arquivo.
        if message == _FINISHED.encode():
            break

        # Escrevendo a mensagem recebida do cliente no arquivo de copia do servidor.
        write_file_process(message, file)
        
        print("Sending message to client...")
        # Enviando uma mensagem para o cliente.
        serverSocket.sendto(message, clientAddress)
        print("Message sent!")
        
        # Esperando uma mensagem do cliente.
        message, clientAddress = serverSocket.recvfrom(_BUFFER_SIZE)
    file.close()

# Funcao que trata os processos do servidor. 
def server():
    serverSocket.bind((_SERVER, _SERVER_PORT))
    print("The server is running!")

    while True:
        print("Waiting for client's message...")
        # Esperando mensagem do cliente.
        message, clientAddress = serverSocket.recvfrom(_BUFFER_SIZE)

        # Verificando se o comando do cliente refere-se ao processamento de um novo arquivo.
        if message.decode() == _FILE:
            # Esperando mensagem do cliente referente ao nome do arquivo a ser criado.
            message, clientAddress = serverSocket.recvfrom(_BUFFER_SIZE)
            # Inicializando o arquivo de copia.
            file = create_file(message)
            # Chamando o processo de recebimento, escrita e envio do arquivo.
            receive_send_file(file)       
        
if __name__ == "__main__":
    server()

