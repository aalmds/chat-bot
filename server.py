import socket
import random
from rdt.RdtReceiver import RdtReceiver
from rdt.RdtSender import RdtSender
from utils import _SERVER, _SERVER_PORT, _BUFFER_SIZE, _CONNECT, _BAN, _BYE, _INBOX, _LIST, _DISCONNECT, _BAN_CONDITION, _BAN_TIMEOUT, current_time, _COLORS, _BAN_COLOR, _CONNECTION_COLOR, _INBOX_COLOR
from threading import Thread, Lock
import time

# Classe do servidor.
class Server():
    def __init__(self):
        # Socket do servidor.
        self.socket_lock = Lock()
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)    

        # Lock do buffer referente a lista de mensagens a serem transmitidas para cada cliente.
        self.buffer_lock = Lock()
        # Mapeamento do endereço do cliente para uma lista de mensagens destinadas ao mesmo.
        self.buffer = {}
        
        # Lock da lista de clientes conectados no chat.
        self.clients_lock = Lock()
        # Mapeamento do endereço do cliente para valores de nome, objetos rdt e cor associada a mensagem.
        self.clients = {}
        
        # Lock da lista de clientes conectados ao chat e seus endereços.
        self.address_lock = Lock()
        # Mapeamento do nome do cliente para o endereço.
        self.addresses = {}

        # Mapeamento dos endereços dos clientes para situação de banimento.
        self.ban = {} 

        # Contador para timeout do ban.
        self.ban_time = -1

    # Função target da thread de envio de mensagens associada a cada cliente conectado ao chat.
    def __send(self, client_address):    
        rdt = self.clients[client_address]['sender']
        connected = True
        
        # Enviando mensagens presentes no buffer do cliente enquanto o mesmo estiver conectado.
        while connected:
            if len(self.buffer[client_address]) != 0:
                if rdt.is_waiting_call():
                    for message in self.buffer[client_address]:
                        # Verificando se o deve ser desconectado.
                        if message == _DISCONNECT:
                            connected = False
                            break
                        # Enviando mensagem para o cliente por um canal confiável.
                        rdt.send(message, client_address)
                   
                    # Resetando a lista de mensagens do cliente.
                    self.buffer_lock.acquire()
                    self.buffer[client_address] = []
                    self.buffer_lock.release()
        
        # Deletando a ocorrência do cliente atual para todos as listas associadas a conexão do mesmo.
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

    # Função para formação padronizada da mensagem.
    def __create_message(self, client_address, message):
        return "[" + current_time() + "] " + self.clients[client_address]['name'] + ': ' + message
    
    # Função para a atualização de um buffer em específico.
    def __update_specific_buffer(self, client_address, message):
        # Adicionando uma mensagem específica ao buffer do cliente.
        self.buffer_lock.acquire()
        self.buffer[client_address].append(message)
        self.buffer_lock.release()
        
    # Função referente ao comando de conexão ao chat.
    def __connect_new_client(self, message, client_address):
        name = message.split("hi, meu nome eh ")[-1]

        # Verificando se o nome escolhido pelo cliente não está está sendo usado.
        if name in self.addresses.keys():
            print(f"O cliente de endereço {client_address} tentou se conectar, mas @{name} já está em uso!")
            return

        # Verificando se o cliente não foi banido.
        if name in self.ban.keys() and self.ban[name] == 'ban':
            print(f"@{name} tentou se conectar, mas está banido!")
            return

        print(f"@{name} se conectou ao chat!")
        
        # Adicionado o cliente nas listas de clientes conectados do servidor.
        self.clients_lock.acquire()
        self.clients[client_address] = {
            'name': name, 
            'sender': RdtSender(self.server_socket), 
            'receiver': RdtReceiver(self.server_socket, '1'),
            'color': random.choice(_COLORS)
        }
        self.clients_lock.release()

        self.addresses[name] = client_address

        # Atualizando o buffer dos clientes com uma mensagem indicando a nova conexão.
        self.__broadcast(client_address, "@" + name + " entrou na sala.", _CONNECTION_COLOR)

        # Inicializando o buffer do novo cliente.
        self.buffer_lock.acquire()
        self.buffer[client_address] = []
        self.buffer_lock.release()

        # Incializando a thread de envio associada ao cliente.
        thread = Thread(target=self.__send, args=(client_address,))
        thread.daemon = True
        thread.start()

    # Função referente ao comando de deconexão do chat.
    def __bye(self, client_address):
        name = self.clients[client_address]['name']
        print(f"@{name} se desconectou do chat!")

        # Atualizando o buffer dos clientes com um mensagem indicando a desconexão.
        self.__broadcast(client_address, "@" + name + " saiu da sala.", _CONNECTION_COLOR)
        # Atualizando o buffer do cliente que solicitou desconexão para que o mesmo seja desconectado do chat.
        self.__update_specific_buffer(client_address, _DISCONNECT)
    
    # Função referente ao comando de listagens dos clientes conectados oa chat.
    def __list_clients(self, client_address):
        # Formando a mensagem a ser enviada.
        message = '\nLista de usuários:\n'
        for client in self.addresses.keys():
            message += '@' + client + '\n'

        # Atualizando o buffer do cliente que solicitou a lista.
        self.__update_specific_buffer(client_address, message + _INBOX_COLOR)

    # Função referente ao comando de inbox.
    def __inbox(self, client_address, message):
        # Encontrando endereço do cliente para o qual a mensagem deve ser enviada.
        for client in self.addresses.keys():
            size = len(client) + 1
            if ("@" + client) == message[:size]:
                message = message[size+1:]
                # Criando a mensagem de acordo com a padronização.
                message = self.__create_message(client_address, message)
                # Atualizando o buffer do cliente que receberá o inbox.
                self.__update_specific_buffer(self.addresses[client], message + _INBOX_COLOR)
                break

    # Função referente ao comando de banimento.
    def __ban(self, client_address, message):
        client = message[len(_BAN):]    

        # Verificando se o cliente que deve ser banido está conetado e não é o próprio cliente e solicitou banimento. 
        if client in self.addresses.keys() and client != self.clients[client_address]['name']:
            print("@" + client + " recebeu um ban!")
            # Verificando se é a primeira solicitação de banimento do cliente.
            if client not in self.ban.keys():
                # Atualizando o contador de banimentos.
                self.ban[client] = 1
            # Verificando se o cliente já não foi banido.
            elif self.ban[client] != 'ban':
                self.ban[client] += 1
                # Verificando a condição de banimento oficial (2/3 da quantidade de clientes conectados).
                if self.ban[client] >= len(self.clients) * _BAN_CONDITION:
                    self.ban[client] = 'ban'
                    print("@" + client + " foi banido do chat!")
                    # Atualizando o buffer dos clientes com uma mensagem indicando o banimento.
                    self.__broadcast(self.addresses[client], "@" + client + " foi banido da sala.", _BAN_COLOR)
                    # Atualizando o buffer do cliente banido indicando seu banimento.
                    self.__update_specific_buffer(self.addresses[client], "Você foi banido da sala!" + _BAN_COLOR)
                    # Atualizando o buffer do cliente que foi banido para que o mesmo seja desconectado do chat.
                    self.__update_specific_buffer(self.addresses[client], _DISCONNECT)

    # Função referente ao broadcast.
    def __broadcast(self, origin, message, color):
        # Adicionando uma mensagem ao buffer de mensagens de cada cliente, exceto o buffer do cliente que enviou a mensagem.
        self.buffer_lock.acquire()
        for client_address in self.buffer.keys():
            if origin != client_address:
                self.buffer[client_address].append(message + color)
        self.buffer_lock.release()
    
    # Função de inicialização do servidor.
    def run(self):
        # Estabelecendo a conexão do socket.
        self.server_socket.bind((_SERVER, _SERVER_PORT))
        print("O chat está on!")
        
        while True:
            # Criando o rdt receptor do servidor para a recepção confiável das mensagens dos clientes.
            rdt_receiver = RdtReceiver(self.server_socket)
            
            try:
                client_message, client_address = self.server_socket.recvfrom(_BUFFER_SIZE)
            except socket.timeout:
                continue
            
            # Verificando se a mensagem é de ack ou não.
            if '%&%' in client_message.decode():
                seqnum, message, _ = client_message.decode().split('%&%')

                # Verificando se o cliente não está conectado 
                if not client_address in self.clients.keys():   
                    # Recebendo a mensagem do cliente por um protocolo confiável.
                    self.socket_lock.acquire()
                    message, _ = rdt_receiver.receive(client_address, seqnum, message)
                    self.socket_lock.release()
                    
                    # Verificando se o cliente está estabelecendo uma nova conexão.
                    if _CONNECT in message:
                        self.__connect_new_client(message, client_address)
                else:
                    # Recebendo a mensagem do cliente por um protocolo confiável.
                    self.socket_lock.acquire()
                    message, _ = self.clients[client_address]['receiver'].receive(client_address, seqnum, message)
                    self.socket_lock.release()

                    # Verificando o comando recebido e chamando a função referente ao mesmo.
                    if _BYE == message:
                        self.__bye(client_address)
                    elif _LIST == message:
                        self.__list_clients(client_address)
                    elif _INBOX == message[0] and _INBOX != message:
                        self.__inbox(client_address, message)
                    elif _BAN in message[:len(_BAN)]:
                        # Verificando se o comando de ban nunca foi chamado ou se temporizador de banimento já atingiu o timeout.
                        if self.ban_time == -1 or time.time() - self.ban_time >= _BAN_TIMEOUT:  
                            # Resetando o temporizador de ban.
                            self.ban_time = time.time()
                            # Dando broadcast na mensagem.
                            self.__broadcast(client_address, self.__create_message(client_address, message), self.clients[client_address]['color'])
                            # Chamando a função de ban.
                            self.__ban(client_address, message)
                        else:
                            # Atualizando o o buffer do cliente com o aviso referente ao temporizador do ban, caso o timeout não tenha sido atingido, 
                            self.__update_specific_buffer(client_address, "Você não pode solicitar esse comando ainda..." + _BAN_COLOR)
                    else:
                        # Dando broadcast da mensagem recebida.
                        self.__broadcast(client_address, self.__create_message(client_address, message), self.clients[client_address]['color'])
            else:
                lock = self.clients[client_address]['sender'].get_lock()
                # Atribuindo novo valor ao ack que foi recebido do cliente.
                lock.acquire()
                self.clients[client_address]['sender'].set_ack(client_message.decode())
                lock.release()

if __name__ == "__main__":
    server = Server()
    server.run()