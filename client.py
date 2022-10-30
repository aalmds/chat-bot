import socket
from termcolor import colored
from utils import _SERVER, _SERVER_PORT, _BUFFER_SIZE, _CONNECT, current_time
from rdt.RdtSender import RdtSender
from rdt.RdtReceiver import RdtReceiver
from threading import Thread, Lock

# Classe do cliente.
class Client:
    def __init__(self):
        # Socket do cliente.
        self.socket_lock = Lock()
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        # Atributos do rdt.
        self.rdt_sender = RdtSender(self.client_socket)
        self.rdt_receiver = RdtReceiver(self.client_socket)

        # Thread responsável por enviar os pacotes do cliente para o servidor.
        self.ths = Thread(target=self.__send)
        self.ths.daemon = True
                
    # Função target da thread de envio de pacotes pelo cliente.
    def __send(self):
        while True:
            # Obtendo a mensagem do cliente.
            message = input()
            print ("\033[A                             \033[A")
            print(colored(f'[{current_time()}] Você: {message}', attrs=["bold"]))

            # Verificando se o cliente está estabelecendo uma nova conexão.
            if _CONNECT in message:
                # Reiniciando o rdt.
                self.rdt_sender = RdtSender(self.client_socket)
                self.rdt_receiver = RdtReceiver(self.client_socket)
            
            # Enviando a mensagem do cliente por um canal confiável.
            if self.rdt_sender.is_waiting_call():
                self.rdt_sender.send(message + "%&% ", (_SERVER, _SERVER_PORT))              

    # Função de inicialização do cliente.
    def run(self):
        # Inicializando a thread do send.
        self.ths.start()

        while True:
            try:
                message, server_address = self.client_socket.recvfrom(_BUFFER_SIZE)
            except socket.timeout:
                continue
            
            # Verificando se a mensagem é de ack ou não.
            if '%&%' in message.decode():
                seqnum, message, color = message.decode().split('%&%')
                
                # Recebendo a mensagem do servidor de por um protocolo confiável.
                self.socket_lock.acquire()
                message, color = self.rdt_receiver.receive(server_address, seqnum, message, color)
                self.socket_lock.release()
                
                print(colored(str(message), color, attrs=["bold"]))         
            else:
                lock = self.rdt_sender.get_lock()
                lock.acquire()
                # Atribuindo novo valor ao ack.
                self.rdt_sender.set_ack(message.decode())
                lock.release()

if __name__ == "__main__":
    client = Client()
    client.run()
