import socket
import os
from Utils import _SERVER, _SERVER_PORT, _BUFFER_SIZE, _FILE, _FINISHED, write_file_process

serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def create_file(message):
    if not os.path.exists("./server_files"):
        os.mkdir("./server_files")
    
    return open("./server_files/received" + message.decode(), 'wb')

def receive_send_file(file):
    message, clientAddress = serverSocket.recvfrom(_BUFFER_SIZE)
    
    while message:
        if message == _FINISHED.encode():
            break

        write_file_process(message, file)
        
        print("Sending message to client...")
        serverSocket.sendto(message, clientAddress)
        print("Message sent!")
        
        message, clientAddress = serverSocket.recvfrom(_BUFFER_SIZE)
    file.close()

def server():
    serverSocket.bind((_SERVER, _SERVER_PORT))
    print("The server is running!")

    while True:
        try:
            print("Waiting for client's message...")
            message, clientAddress = serverSocket.recvfrom(_BUFFER_SIZE)
        except (socket.error, exc): 
            print("Socket.error - " + exc)
        
        if message.decode() == _FILE:
            message, clientAddress = serverSocket.recvfrom(_BUFFER_SIZE)
            file = create_file(message)
            receive_send_file(file)       
        
if __name__ == "__main__":
    server()

