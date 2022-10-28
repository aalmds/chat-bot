import socket
from RdtReceiver import RdtReceiver
from RdtSender import RdtSender
from Utils import _SERVER, _SERVER_PORT, _BUFFER_SIZE, _CONNECT, _BAN, _BYE, _INBOX, _LIST, time
from threading import Thread, Lock

class Server():
    def __init__(self):
        self.socket_lock = Lock()
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)    

        self.buffer_lock = Lock()
        self.buffer = {}

        self.clients = {}

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

    def __create_message(self, clientAddress, message):
        return "[" + time() + "] " + self.clients[clientAddress]['name'] + ': ' + message

    def __connect_new_client(self, message, clientAddress):
        name = message.split("hi, meu nome eh ")[-1]
        print(f"@{name} se conectou ao chat!")

        self.clients[clientAddress] = {
            'name': name, 
            'sender': RdtSender(self.serverSocket), 
            'receiver': RdtReceiver(self.serverSocket, '1')
        }

        self.__broadcast(clientAddress, "@" + name + " entrou na sala")

        self.buffer_lock.acquire()
        self.buffer[clientAddress] = []
        self.buffer_lock.release()

        thread = Thread(target=self.__send, args=(clientAddress,))
        thread.daemon = True
        thread.start()

    def __bye(self, clientAddress):
        name = self.clients[clientAddress]['name']
        print(f"@{name} se desconectou do chat!")
        self.__broadcast(clientAddress, "@" + name + " saiu da sala")
        del self.clients[clientAddress]

    def __list_clients(self, clientAddress):
        message = '\nLista de usuários:\n'

        for client in self.clients.values():
            message += '@' + str(client['name']) + '\n'

        self.buffer_lock.acquire()
        self.buffer[clientAddress].append(message)
        self.buffer_lock.release()

    def __inbox(self, clientAddress, message):
        for address in self.clients.keys():
            client_name = self.clients[address]['name']
            size = len(client_name) + 1
            if ("@" + client_name) == message[:size]:
                message = message[size+1:]
                message = self.__create_message(clientAddress, message)
                
                self.buffer_lock.acquire()
                self.buffer[address].append(message)
                self.buffer_lock.release()
                
                break

    def __broadcast(self, origin, message):
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
                seqnum, message = clientMessage.decode().split('%&%')
                if not clientAddress in self.clients.keys():             
                    self.socket_lock.acquire()
                    message = rdt_receiver.receive(clientAddress, seqnum, message)
                    self.socket_lock.release()
                
                    if _CONNECT in message:
                        self.__connect_new_client(message, clientAddress)
                       
                else:
                    self.socket_lock.acquire()
                    message = self.clients[clientAddress]['receiver'].receive(clientAddress, seqnum, message)
                    self.socket_lock.release()

                    if _BYE == message:
                        self.__bye(clientAddress)
                    elif _LIST == message:
                        self.__list_clients(clientAddress)
                    elif _INBOX in message[0]:
                        self.__inbox(clientAddress, message)
                    elif _BAN in message[:len(_BAN)]:
                        print('ban')
                    else:
                        message = self.__create_message(clientAddress, message)
                        self.__broadcast(clientAddress, message)
            else:
                self.clients[clientAddress]['sender'].set_ack(clientMessage.decode())
                    
if __name__ == "__main__":
    server = Server()
    server.run()


    
