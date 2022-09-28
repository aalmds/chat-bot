from Utils import _BUFFER_SIZE
from threading import Timer

class RdtSender:
    def __init__(self, socket):
        self.socket = socket
        self.sequence_number = '0'
        # Define estado de espera pela chamada de cima
        self.waiting = True
        
    def __check_ack(self, ack):
        return ack == self.sequence_number

    def __update_seqnum(self):
        self.sequence_number = '0' if self.sequence_number == '1' else '1' 
    
    def __timeout(self, chunk, address):
        print("Timeout!")
        # Retransmite pacote
        self.send(chunk, address)

    def __wait_ack(self, chunk, address):
        timer = Timer(10.0, self.__timeout, args = (chunk, address))
        timer.start()
        
        ack, address = self.socket.recvfrom(_BUFFER_SIZE)
        print("Waiting for ack", self.sequence_number)

        if self.__check_ack(ack.decode()):
            print("The ack is correct!")
            print("_____________\n")
            # Desliga timer
            timer.cancel()
            # Atualiza o numero de sequencia
            self.__update_seqnum()
            # Volta para o estado de espera, ou seja, pode enviar dados
            self.waiting = True
            
    def send(self, chunk, address):
        # Sai do estado de espera
        self.waiting = False

        pkt = self.sequence_number + "," + chunk
        print(f"Pkt was built with: ({self.sequence_number}, \"{chunk}\")")

        self.socket.sendto(pkt.encode(), address)
        self.__wait_ack(chunk, address)

    def is_waiting_call(self):
        return self.waiting
