import socket
from RdtReceiver import RdtReceiver
from RdtSender import RdtSender
from Utils import _SERVER, _SERVER_PORT, _BUFFER_SIZE


class Server():
    def __init__(self):
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.rdt_sender = RdtSender(self.serverSocket)
        self.rdt_receiver = RdtReceiver(self.serverSocket)
   
    def run(self):
        self.serverSocket.bind((_SERVER, _SERVER_PORT))
        print("The server is running!")

        print("Waiting for client's message...")
        message, clientAddress = self.serverSocket.recvfrom(_BUFFER_SIZE)
        seqnum, data = message.decode().split(',')

        print(f"Pkt received with seqnum = {seqnum} and data = {data}")
        self.rdt_receiver.receive(seqnum, clientAddress)
        
        a = 5
        while a:
            a -= 1
            if self.rdt_sender.is_waiting_call():
                print("Sending new package in server...")
                self.rdt_sender.send("Testing server", clientAddress)
        
if __name__ == "__main__":
    server = Server()
    server.run()


