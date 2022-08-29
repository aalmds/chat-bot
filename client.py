import socket 
from Utils import _SERVER, _SERVER_PORT, _BUFFER_SIZE, _FILE, _FINISHED, write_file_process

clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Funcao que envia um comando para o servidor indicando qual acao deve ser tomada:
#   - _FILE indicando que novo arquivo deve ser criado no servidor e qual o nome do mesmo.
#   - _FINISHED indicando que o arquivo que estava sendo escrito terminou. 
def define_command(command, name = ""):
    clientSocket.sendto(command.encode(), (_SERVER, _SERVER_PORT))
    if name != "":
        clientSocket.sendto(name.encode(), (_SERVER, _SERVER_PORT))
    
# Funcao que gerencia o envio, recebimento e escrita de cada um dos chunks do arquivo.
def send_receive_file(chunk, file):
    print("Sending message to server...")
    # Enviando uma mensagem para o servidor.
    clientSocket.sendto(chunk, (_SERVER, _SERVER_PORT))
    print("Message sent!")

    try:
        print("Waiting server response...")
        # Esperando uma mensagem do servidor.
        message, clientAddress = clientSocket.recvfrom(_BUFFER_SIZE)
        # Escrevendo a mensagem recebida do servidor no arquivo de copia do cliente.
        write_file_process(message, file)
    except IOError:
        print("Error in communication with server.")

# Funcao que gerencia os arquivos do cliente.
def file_process(extension):
    # Abrindo o arquivo a ser lido e enviado.
    file = open("./client_files/Teste" + extension, 'rb')
    chunk = file.read(_BUFFER_SIZE)
    # Inicializando a copia do arquivo que sera devolvido pelo servidor.
    new_file = open("./client_files/received" + extension, 'wb')

    # Percorrendo o arquivo a ser enviado em chunks do tamanho de _BUFFER_SIZE.
    while chunk:
        # Chamando o tratamento para o chunk atual.
        send_receive_file(chunk, new_file)
        print("Reading new chunk!")
        chunk = file.read(_BUFFER_SIZE)

    # Enviando um comando para o servidor.
    define_command(_FINISHED)
    print("File finished!")   
    file.close()
    new_file.close()

# Funcao que trata os processos do cliente. 
def client():
    print("The client is on!")

    # Enviando um comando para o servidor.
    define_command(_FILE, "TXT.txt")
    # Chamando o gerenciamento de envio, escrita e recebimento do arquivo .txt.
    file_process("TXT.txt")

    # Enviando um comando para o servidor.
    define_command(_FILE, "PDF.pdf")
    # Chamando o gerenciamento de envio, escrita e recebimento do arquivo .pdf.
    file_process("PDF.pdf")

    clientSocket.close()

if __name__ == "__main__":
    client()