import socket
from Utils import _SERVER, _SERVER_PORT, _BUFFER_SIZE

def server():
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    serverSocket.bind((_SERVER, _SERVER_PORT))
    print("The server is running!")

    count = 1
    while True:
        print("Waiting for client's message...")
        message, clientAddress = serverSocket.recvfrom(_BUFFER_SIZE)
        print("Sending message to client...")
        serverSocket.sendto(message, clientAddress)
        print("Message sent!")       
        
if __name__ == "__main__":
    server()

