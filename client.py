import socket
from termcolor import colored
from Utils import _SERVER, _SERVER_PORT, _BUFFER_SIZE, time
from RdtSender import RdtSender
from RdtReceiver import RdtReceiver
from threading import Thread, Lock

class Client:
    def __init__(self):
        self.socket_lock = Lock()
        self.clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        self.rdt_sender = RdtSender(self.clientSocket)
        self.rdt_receiver = RdtReceiver(self.clientSocket)

        self.ths = Thread(target=self.__send)
        self.ths.daemon = True
                
    def __send(self):
        while True:
            message = input()
            print ("\033[A                             \033[A")
            print(f'[{time()}] Você: {message}')
            if self.rdt_sender.is_waiting_call():
                self.rdt_sender.send(message, (_SERVER, _SERVER_PORT)) 

    def run(self):
        self.ths.start()

        while True:
            try:
                message, serverAddress = self.clientSocket.recvfrom(_BUFFER_SIZE)
            except socket.timeout:
                continue

            if '%&%' in message.decode():
                seqnum, message = message.decode().split('%&%')
                
                self.socket_lock.acquire()
                message = self.rdt_receiver.receive(serverAddress, seqnum, message)
                self.socket_lock.release()
                
                print(colored(str(message), 'cyan'))         

            else:
                lock = self.rdt_sender.get_lock()
                lock.acquire()
                self.rdt_sender.set_ack(message.decode())
                lock.release()

if __name__ == "__main__":
    client = Client()
    client.run()
