import socket
from RdtReceiver import RdtReceiver
from RdtSender import RdtSender
from Utils import _SERVER, _SERVER_PORT, _BUFFER_SIZE, _COMMANDS
from threading import Thread, Lock

class Server():
    def __init__(self):
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)    
        self.lock = Lock()
        self.clients = {}

    def __thread_server(self, clientAddress):
        print(f'A new thread for client {clientAddress} was created!')
        rdt_sender = RdtSender(self.serverSocket)
        rdt_receiver = RdtReceiver('1', self.serverSocket)

        while True:
            message, address = self.serverSocket.recvfrom(_BUFFER_SIZE)
            if clientAddress == address:
                seqnum, message = message.decode().split('%&%')
                rdt_receiver.receive(clientAddress, seqnum)
                print(clientAddress, address, message + '\n')

                if rdt_sender.is_waiting_call():
                    with self.lock:
                        for client in self.clients.values():
                            if client != clientAddress:
                                rdt_sender.send(message,client)

    def run(self):
        self.serverSocket.bind((_SERVER, _SERVER_PORT))
        
        while True:
            rdt_receiver = RdtReceiver('0', self.serverSocket)
            clientMessage, clientAddress = self.serverSocket.recvfrom(_BUFFER_SIZE)
            if not clientAddress in self.clients.values():
                print(f'New client {clientAddress} connect to chat!\n')
                seqnum, message = clientMessage.decode().split('%&%')
                rdt_receiver.receive(clientAddress, seqnum)
            
                if _COMMANDS[0] in message:
                    name = message.split("hi, meu nome eh ")[-1]
                    self.clients[name] = clientAddress
                    thread = Thread(target=self.__thread_server, args=(clientAddress,))
                    thread.start()


if __name__ == "__main__":
    server = Server()
    server.run()
