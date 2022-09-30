import socket
from Utils import _SERVER, _SERVER_PORT
from RdtSender import RdtSender

class Client:
    def __init__(self):
        self.clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.rdt_sender = RdtSender(self.clientSocket)

    def run(self):
        print("The client is on!\n")

        for i in range(0,4):
            if self.rdt_sender.is_waiting_call():
                print("Sending new package in client...")
                # Enviando a mensagem por um canal confiável de transferência de dados.
                self.rdt_sender.send("Hello from client!", (_SERVER, _SERVER_PORT))

        self.clientSocket.close()

if __name__ == "__main__":
    client = Client()
    client.run()