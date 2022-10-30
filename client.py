import socket
from termcolor import colored
from utils import _SERVER, _SERVER_PORT, _BUFFER_SIZE, _CONNECT, current_time
from rdt.RdtSender import RdtSender
from rdt.RdtReceiver import RdtReceiver
from threading import Thread, Lock

class Client:
    def __init__(self):
        self.socket_lock = Lock()
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        self.rdt_sender = RdtSender(self.client_socket)
        self.rdt_receiver = RdtReceiver(self.client_socket)

        self.ths = Thread(target=self.__send)
        self.ths.daemon = True
                
    def __send(self):

        while True:
            message = input()
            print ("\033[A                             \033[A")
            print(colored(f'[{current_time()}] Você: {message}', attrs=["bold"]))

            if _CONNECT in message:
                self.rdt_sender = RdtSender(self.client_socket)
                self.rdt_receiver = RdtReceiver(self.client_socket)

            if self.rdt_sender.is_waiting_call():
                self.rdt_sender.send(message + "%&% ", (_SERVER, _SERVER_PORT))              

    def run(self):
        self.ths.start()

        while True:
            try:
                message, server_address = self.client_socket.recvfrom(_BUFFER_SIZE)
            except socket.timeout:
                continue

            if '%&%' in message.decode():
                seqnum, message, color = message.decode().split('%&%')
                
                self.socket_lock.acquire()
                message, color = self.rdt_receiver.receive(server_address, seqnum, message, color)
                self.socket_lock.release()
                
                print(colored(str(message), color, attrs=["bold"]))         

            else:
                lock = self.rdt_sender.get_lock()
                lock.acquire()
                self.rdt_sender.set_ack(message.decode())
                lock.release()

if __name__ == "__main__":
    client = Client()
    client.run()
