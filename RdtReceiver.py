class RdtReceiver:
    def __init__(self, socket):
        self.sequence_number = '0'
        self.socket = socket

    def __check_pkt(self, seqnum):
        return seqnum == self.sequence_number

    def __nott(self):
        return '0' if self.sequence_number == '1' else '1' 

    def receive(self, seqnum, address):
        if self.__check_pkt(seqnum):
            # Recebeu o pacote esperado
            ack = self.sequence_number.encode()
            self.socket.sendto(ack, address)
            # Passa a esperar por outro pacote
            self.sequence_number = self.__nott()
            print("Package is correct, sending ack", ack.decode())
            print("_____________\n")
        else:
            # Recebeu um duplicata
            ack = self.__nott().encode()
            # Reenvia ack do anterior, confirmando que ele já tinha sido recebido
            self.socket.sendto(ack, address)
            print("Duplicate detected, resending ack", ack.decode())
            print("_____________\n")