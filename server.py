import socket
from RdtReceiver import RdtReceiver
from RdtSender import RdtSender
from Utils import _SERVER, _SERVER_PORT, _BUFFER_SIZE


class Server():
    def __init__(self):
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.rdt_receiver = RdtReceiver(self.serverSocket)
        self.rdt_sender = RdtSender(self.serverSocket)

    def run(self):
        self.serverSocket.bind((_SERVER, _SERVER_PORT))
        print("The server is running!\n")

        for i in range(0, 2):
            print("Waiting for client's message...")
            message, clientAddress = self.serverSocket.recvfrom(_BUFFER_SIZE)
            seqnum, _ = message.decode().split(',')
            # Recebendo a mensagem por um canal confiável de transferência de dados.
            self.rdt_receiver.receive(clientAddress, seqnum)

            # Enviando um novo pacote para o cliente caso o transmissor esteja disponível para enviar.
            if self.rdt_sender.is_waiting_call():
                print("Sending new package in server...")
                # Enviando a mensagem por um canal confiável de transferência de dados.
                self.rdt_sender.send("Hello from server!", clientAddress)


if __name__ == "__main__":
    server = Server()
    server.run()
