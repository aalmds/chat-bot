from http import client
import socket
from RdtReceiver import RdtReceiver
from RdtSender import RdtSender
from Utils import _SERVER, _SERVER_PORT, _BUFFER_SIZE, _CONNECT, _BAN, _BYE, _INBOX, _LIST, time, _DISCONNECT, _BAN_CONDITION, _BAN_TIMEOUT
from threading import Thread, Lock

class Server():
    def __init__(self):
        self.socket_lock = Lock()
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)    

        self.buffer_lock = Lock()
        self.buffer = {}

        self.clients = {}
        self.ban = {} 

    def __send(self, client_address):    
        rdt = self.clients[client_address]['sender']
        connected = True

        while connected:
            if len(self.buffer[client_address]) != 0:
                if rdt.is_waiting_call():
                    for message in self.buffer[client_address]:
                        if message == _DISCONNECT:
                            connected = False
                        else:
                            rdt.send(message, client_address)
                    self.buffer[client_address] = []
        
        del self.clients[client_address]

        self.buffer_lock.acquire()
        del self.buffer[client_address]
        self.buffer_lock.release()
        return

    def __create_message(self, client_address, message):
        return "[" + time() + "] " + self.clients[client_address]['name'] + ': ' + message
    
    def __update_specific_buffer(self, client_address, message):
        self.buffer_lock.acquire()
        self.buffer[client_address].append(message)
        self.buffer_lock.release()
        
    def __connect_new_client(self, message, client_address):
        name = message.split("hi, meu nome eh ")[-1]

        if name in self.ban.keys() and self.ban[name] == 'ban':
            print(f"@{name} tentou se conectar, mas está banido!")
            return

        print(f"@{name} se conectou ao chat!")

        self.clients[client_address] = {
            'name': name, 
            'sender': RdtSender(self.serverSocket), 
            'receiver': RdtReceiver(self.serverSocket, '1')
        }

        self.__broadcast(client_address, "@" + name + " entrou na sala")

        self.buffer_lock.acquire()
        self.buffer[client_address] = []
        self.buffer_lock.release()

        thread = Thread(target=self.__send, args=(client_address,))
        thread.daemon = True
        thread.start()

    def __bye(self, client_address):
        name = self.clients[client_address]['name']
        print(f"@{name} se desconectou do chat!")
        self.__broadcast(client_address, "@" + name + " saiu da sala")

        self.__update_specific_buffer(client_address, _DISCONNECT)
        
    def __list_clients(self, client_address):
        message = '\nLista de usuários:\n'

        for client in self.clients.values():
            message += '@' + str(client['name']) + '\n'
        self.__update_specific_buffer(client_address, message)

    def __inbox(self, client_address, message):
        for address in self.clients.keys():
            client_name = self.clients[address]['name']
            size = len(client_name) + 1
            if ("@" + client_name) == message[:size]:
                message = message[size+1:]
                message = self.__create_message(client_address, message)
                self.__update_specific_buffer(address, message)
                break

    def __broadcast(self, origin, message):
        self.buffer_lock.acquire()
        for client_address in self.buffer.keys():
            if origin != client_address:
                self.buffer[client_address].append(message)
        self.buffer_lock.release()

    def __ban(self, message):
        client = message[len(_BAN):]    
                
        print("@" + client + " recebeu um ban!")
        if client not in self.ban.keys():
            self.ban[client] = 1
        elif self.ban[client] != 'ban':
            self.ban[client] += 1
            if self.ban[client] >= len(self.clients) * _BAN_CONDITION:
                self.ban[client] = 'ban'
                print("@" + client + " foi banido da sala!")
                for address in self.clients.keys():
                    client_name = self.clients[address]['name']
                    if client_name == client:
                        self.__broadcast(address, "@" + client + " foi banido da sala")
                        self.__update_specific_buffer(address, "Você foi banido da sala")
                        self.__update_specific_buffer(address, _DISCONNECT)
                        break
                                
        
    def run(self):
        self.serverSocket.bind((_SERVER, _SERVER_PORT))
        print("O chat está on!")
        
        while True:
            rdt_receiver = RdtReceiver(self.serverSocket)
            
            try:
                clientMessage, client_address = self.serverSocket.recvfrom(_BUFFER_SIZE)
            except socket.timeout:
                continue

            if '%&%' in clientMessage.decode():
                seqnum, message = clientMessage.decode().split('%&%')
                if not client_address in self.clients.keys():   
                    self.socket_lock.acquire()
                    message = rdt_receiver.receive(client_address, seqnum, message)
                    self.socket_lock.release()
                    
                    if _CONNECT in message:
                        self.__connect_new_client(message, client_address)
                else:
                    self.socket_lock.acquire()
                    message = self.clients[client_address]['receiver'].receive(client_address, seqnum, message)
                    self.socket_lock.release()

                    if _BYE == message:
                        self.__bye(client_address)
                    elif _LIST == message:
                        self.__list_clients(client_address)
                    elif _INBOX == message[0] and _INBOX != message:
                        self.__inbox(client_address, message)
                    elif _BAN in message[:len(_BAN)]:
                        client_message = self.__create_message(client_address, message)
                        self.__broadcast(client_address, client_message)
                        self.__ban(message)
                    else:
                        message = self.__create_message(client_address, message)
                        self.__broadcast(client_address, message)
            else:
                lock = self.clients[client_address]['sender'].get_lock()
                lock.acquire()
                self.clients[client_address]['sender'].set_ack(clientMessage.decode())
                lock.release()
                    
if __name__ == "__main__":
    server = Server()
    server.run()