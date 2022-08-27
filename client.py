import socket 
from Utils import _SERVER, _SERVER_PORT, _BUFFER_SIZE

clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def client_server_communication(chunk, file):
    print("Sending message to server...")
    clientSocket.sendto(chunk, (_SERVER, _SERVER_PORT))
    print("Message sent!")

    try:
        print("Waiting server response...")
        message, clientAddress = clientSocket.recvfrom(_BUFFER_SIZE)
        try:          
            print("Writing file...")      
            file.write(message)
        except IOError:
            print("Error in writing file.")
    except IOError:
        print("Error in communication with server.")

def send(extension):
    file = open("./files/Teste" + extension, 'rb')
    chunk = file.read(_BUFFER_SIZE)
    new_file = open("./files/received" + extension, 'wb')

    while chunk:
        client_server_communication(chunk, new_file)
        print("Reading new chunk!")
        chunk = file.read(_BUFFER_SIZE)

    print("File finished!")   
    file.close()
    new_file.close()
    
def client():
    print("The client is on!")
    send("TXT.txt")
    send("PDF.pdf")
    clientSocket.close()

if __name__ == "__main__":
    client()

