import socket 
from Utils import _SERVER, _SERVER_PORT, _BUFFER_SIZE, _FILE, _FINISHED, write_file_process

clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def define_command(command, name = ""):
    clientSocket.sendto(command.encode(), (_SERVER, _SERVER_PORT))
    if name != "":
        clientSocket.sendto(name.encode(), (_SERVER, _SERVER_PORT))
    
def send_receive_file(chunk, file):
    print("Sending message to server...")
    clientSocket.sendto(chunk, (_SERVER, _SERVER_PORT))
    print("Message sent!")

    try:
        print("Waiting server response...")
        message, clientAddress = clientSocket.recvfrom(_BUFFER_SIZE)
        write_file_process(message, file)
    except (socket.error, exc): 
        print("Socket.error - " + exc)

def file_process(extension):
    file = open("./client_files/Teste" + extension, 'rb')
    chunk = file.read(_BUFFER_SIZE)
    new_file = open("./client_files/received" + extension, 'wb')

    while chunk:
        send_receive_file(chunk, new_file)
        print("Reading new chunk!")
        chunk = file.read(_BUFFER_SIZE)

    define_command(_FINISHED)
    print("File finished!")   
    file.close()
    new_file.close()

def client():
    print("The client is on!")

    define_command(_FILE, "TXT.txt")
    file_process("TXT.txt")

    define_command(_FILE, "PDF.pdf")
    file_process("PDF.pdf")

    clientSocket.close()

if __name__ == "__main__":
    client()