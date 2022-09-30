import socket
from RdtReceiver import RdtReceiver
from Utils import _SERVER, _SERVER_PORT

class Server():
    def __init__(self):
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.rdt_receiver = RdtReceiver(self.serverSocket)
   
    def run(self):
        self.serverSocket.bind((_SERVER, _SERVER_PORT))
        print("The server is running!\n")
        
        while True:
            print("Waiting for client's message...")
            # Recebendo a mensagem por um canal confiável de transferência de dados.
            self.rdt_receiver.receive()

if __name__ == "__main__":
    server = Server()
    server.run()


