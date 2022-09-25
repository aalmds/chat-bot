import socket
from Utils import _SERVER, _SERVER_PORT
from RdtSender import RdtSender
from RdtReceiver import RdtReceiver


class Client:
    def __init__(self):
        self.clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.rdt_sender = RdtSender(self.clientSocket)
        self.rdt_receiver = RdtReceiver(self.clientSocket)

    def run(self):
        print("The client is on!")

        a = 5
        while a:
            a -= 1
            self.rdt_sender.send("testing", (_SERVER, _SERVER_PORT))       

            # message, serverAddress = self.clientSocket.recvfrom(_BUFFER_SIZE)
            # seqnum, data = message.decode().split(',')
            # print(f"seqnum = {seqnum}, data = {data}")
            # if serverAddress == (_SERVER, _SERVER_PORT):
            #     print("É igual")
            # self.rdt_receiver.receive(seqnum, (_SERVER, _SERVER_PORT))
        
        self.clientSocket.close()

if __name__ == "__main__":
    client = Client()
    client.run()