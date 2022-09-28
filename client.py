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

        a = 5
        while a:
            a -= 1  
            if self.rdt_sender.is_waiting_call():
                print("Sending new package in client...")
                self.rdt_sender.send("Hello from client!", (_SERVER, _SERVER_PORT))  

            message, serverAddress = self.clientSocket.recvfrom(_BUFFER_SIZE)
            seqnum, data = message.decode().split(',')
            print(f"Package received with: ({seqnum}, \"{data}\"")
            self.rdt_receiver.receive(seqnum, (_SERVER, _SERVER_PORT))
        
        self.clientSocket.close()

if __name__ == "__main__":
    client = Client()
    client.run()