import socket
from rdt.RdtReceiver import RdtReceiver
from rdt.RdtSender import RdtSender
from utils import _SERVER, _SERVER_PORT, _BUFFER_SIZE, _CONNECT, _BAN, _BYE, _INBOX, _LIST, _DISCONNECT, _BAN_CONDITION, _BAN_TIMEOUT, current_time
from threading import Thread, Lock
import time

class Server():
    def __init__(self):
        # Socket do servidor.
        self.socket_lock = Lock()
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)    

        self.buffer_lock = Lock()
        self.buffer = {}
        
        # Mapeamento do endereço do cliente como chave para valores de nome e objetos rdt.
        self.clients_lock = Lock()
        self.clients = {}
        
        # Mapeamento do nome do nome do cliente para o endereço.
        self.address_lock = Lock()
        self.addresses = {}

        # Mapeamento dos endereços dos clientes como chaves para situação de banimento.
        self.ban = {} 

        # Contador para timeout do ban.
        self.ban_time = -1

    def __send(self, client_address):    
        rdt = self.clients[client_address]['sender']
        connected = True

        while connected:
            if len(self.buffer[client_address]) != 0:
                if rdt.is_waiting_call():
                    for message in self.buffer[client_address]:
                        if message == _DISCONNECT:
                            connected = False
                            break
                        rdt.send(message, client_address)
                   
                    self.buffer_lock.acquire()
                    self.buffer[client_address] = []
                    self.buffer_lock.release()
        
        self.address_lock.acquire()
        del self.addresses[self.clients[client_address]['name']]
        self.address_lock.release()

        self.clients_lock.acquire()
        del self.clients[client_address]
        self.clients_lock.release()
        
        self.buffer_lock.acquire()
        del self.buffer[client_address]
        self.buffer_lock.release()
    
        return

    def __create_message(self, client_address, message):
        return "[" + current_time() + "] " + self.clients[client_address]['name'] + ': ' + message
    
    def __update_specific_buffer(self, client_address, message):
        self.buffer_lock.acquire()
        self.buffer[client_address].append(message)
        self.buffer_lock.release()
        
    def __connect_new_client(self, message, client_address):
        name = message.split("hi, meu nome eh ")[-1]

        if name in self.addresses.keys():
            print(f"O cliente de endereço {client_address} tentou se conectar, mas @{name} já está em uso!")
            return

        if name in self.ban.keys() and self.ban[name] == 'ban':
            print(f"@{name} tentou se conectar, mas está banido!")
            return

        print(f"@{name} se conectou ao chat!")

        self.clients_lock.acquire()
        self.clients[client_address] = {
            'name': name, 
            'sender': RdtSender(self.server_socket), 
            'receiver': RdtReceiver(self.server_socket, '1')
        }
        self.clients_lock.release()

        self.addresses[name] = client_address

        self.__broadcast(client_address, "@" + name + " entrou na sala.")

        self.buffer_lock.acquire()
        self.buffer[client_address] = []
        self.buffer_lock.release()

        thread = Thread(target=self.__send, args=(client_address,))
        thread.daemon = True
        thread.start()

    def __bye(self, client_address):
        name = self.clients[client_address]['name']
        print(f"@{name} se desconectou do chat!")

        self.__broadcast(client_address, "@" + name + " saiu da sala.")
        self.__update_specific_buffer(client_address, _DISCONNECT)
        
    def __list_clients(self, client_address):
        message = '\nLista de usuários:\n'

        for client in self.addresses.keys():
            message += '@' + client + '\n'

        self.__update_specific_buffer(client_address, message)

    def __inbox(self, client_address, message):
        for client in self.addresses.keys():
            size = len(client) + 1
            if ("@" + client) == message[:size]:
                message = message[size+1:]
                message = self.__create_message(client_address, message)
                self.__update_specific_buffer(self.addresses[client], message)
                break

    def __ban(self, message):
        client = message[len(_BAN):]    
                
        if client in self.addresses.keys():
            print("@" + client + " recebeu um ban!")
            if client not in self.ban.keys():
                self.ban[client] = 1
            elif self.ban[client] != 'ban':
                self.ban[client] += 1

                if self.ban[client] >= len(self.clients) * _BAN_CONDITION:
                    self.ban[client] = 'ban'
                    print("@" + client + " foi banido do chat!")
                    self.__broadcast(self.addresses[client], "@" + client + " foi banido da sala.")
                    self.__update_specific_buffer(self.addresses[client], "Você foi banido da sala!")
                    self.__update_specific_buffer(self.addresses[client], _DISCONNECT)

    def __broadcast(self, origin, message):
        self.buffer_lock.acquire()
        for client_address in self.buffer.keys():
            if origin != client_address:
                self.buffer[client_address].append(message)
        self.buffer_lock.release()
        
    def run(self):
        self.server_socket.bind((_SERVER, _SERVER_PORT))
        print("O chat está on!")
        
        while True:
            rdt_receiver = RdtReceiver(self.server_socket)
            
            try:
                client_message, client_address = self.server_socket.recvfrom(_BUFFER_SIZE)
            except socket.timeout:
                continue

            if '%&%' in client_message.decode():
                seqnum, message = client_message.decode().split('%&%')
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
                        if self.ban_time == -1 or time.time() - self.ban_time >= _BAN_TIMEOUT:  
                            self.ban_time = time.time()
                            self.__broadcast(client_address, self.__create_message(client_address, message))
                            self.__ban(message)
                        else:
                            self.__update_specific_buffer(client_address, "Você não pode solicitar esse comando ainda...")
                    else:
                        self.__broadcast(client_address, self.__create_message(client_address, message))
            else:
                lock = self.clients[client_address]['sender'].get_lock()
                lock.acquire()
                self.clients[client_address]['sender'].set_ack(client_message.decode())
                lock.release()
                    
if __name__ == "__main__":
    server = Server()
    server.run()