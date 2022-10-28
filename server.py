import socket
from RdtReceiver import RdtReceiver
from RdtSender import RdtSender
from Utils import _SERVER, _SERVER_PORT, _BUFFER_SIZE, _COMMANDS, time
from threading import Thread, Lock

class Server():
    def __init__(self):
        self.socket_lock = Lock()
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)    
        
        self.clients = {}

        self.buffer_lock = Lock()
        self.buffer = {}

        self.threads = []

    def __send(self, clientAddress):    
        rdt = self.clients[clientAddress]['sender']
        while True:
            self.buffer_lock.acquire()
            if len(self.buffer[clientAddress]) != 0:
                if rdt.is_waiting_call():
                    for message in self.buffer[clientAddress]:
                        rdt.send(message, clientAddress)
                    self.buffer[clientAddress] = []
            self.buffer_lock.release()

    def __update_buffer(self, origin, message):
        self.buffer_lock.acquire()
        for clientAddress in self.buffer.keys():
            if origin != clientAddress:
                self.buffer[clientAddress].append(message)

        self.buffer_lock.release()

    def run(self):
        self.serverSocket.bind((_SERVER, _SERVER_PORT))

        print("O chat está on!")
        
        while True:
            rdt_receiver = RdtReceiver(self.serverSocket)
            self.socket_lock.acquire()
            
            try:
                clientMessage, clientAddress = self.serverSocket.recvfrom(_BUFFER_SIZE)
            except socket.timeout:
                continue

            self.socket_lock.release()
            if '%&%' in clientMessage.decode():
                addresses = self.clients.keys()
                if not clientAddress in addresses:
                    seqnum, message = clientMessage.decode().split('%&%')
                    
                    self.socket_lock.acquire()
                    rdt_receiver.receive(clientAddress, seqnum, message)
                    self.socket_lock.release()
                
                    if _COMMANDS[0] in message:
                        name = message.split("hi, meu nome eh ")[-1]

                        print(f"@{name} se conectou ao chat!")

                        self.clients[clientAddress] = {
                            'name': name, 
                            'sender': RdtSender(self.serverSocket), 
                            'receiver': RdtReceiver(self.serverSocket, '1')
                        }

                        self.__update_buffer(clientAddress, "@" + name + " entrou na sala")

                        self.buffer_lock.acquire()
                        self.buffer[clientAddress] = []
                        self.buffer_lock.release()

                        self.threads.append(Thread(target=self.__send, args=(clientAddress,)))
                        self.threads[-1].daemon = True
                        self.threads[-1].start()
                else:
                    seqnum, message = clientMessage.decode().split('%&%')
                    self.socket_lock.acquire()
                    message = self.clients[clientAddress]['receiver'].receive(clientAddress, seqnum, message)
                    self.socket_lock.release()

                    message = "[" + time() + "] " + self.clients[clientAddress]['name'] + ': ' + message
                    self.__update_buffer(clientAddress, message)
            else:
                self.clients[clientAddress]['sender'].set_ack(clientMessage.decode())
                    
if __name__ == "__main__":
    server = Server()
    server.run()


    
