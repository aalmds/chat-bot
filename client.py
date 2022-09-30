import socket
from Utils import _SERVER, _SERVER_PORT, _BUFFER_SIZE
from RdtSender import RdtSender
from RdtReceiver import RdtReceiver


class Client:
    def __init__(self):
        self.clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.rdt_sender = RdtSender(self.clientSocket)
        self.rdt_receiver = RdtReceiver(self.clientSocket)

    def run(self):
        print("The client is on!\n")

        for i in range(0, 2):
            # Enviando um novo pacote para o servidor caso o transmissor esteja dinsponível para enviar.
            if self.rdt_sender.is_waiting_call():
                print("Sending new package in client...")
                # Enviando a mensagem por um canal confiável de transferência de dados.
                self.rdt_sender.send("Hello from client!",
                                     (_SERVER, _SERVER_PORT))

            print("Waiting for server's message...")
            message, serverAddress = self.clientSocket.recvfrom(_BUFFER_SIZE)
            seqnum, _ = message.decode().split(',')
            # Recebendo a mensagem por um canal confiável de transferência de dados.
            self.rdt_receiver.receive(serverAddress, seqnum)

        self.clientSocket.close()


if __name__ == "__main__":
    client = Client()
    client.run()
