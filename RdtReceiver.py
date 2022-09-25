class RdtReceiver:
    def __init__(self, socket):
        self.sequence_number = '0'
        self.socket = socket

    def check_pkt(self, seqnum):
        return seqnum == self.sequence_number

    def nott(self):
        return '0' if self.sequence_number == '1' else '1' 

    def receive(self, seqnum, address):
        if self.check_pkt(seqnum):
            # recebeu o pacote esperado
            ack = self.sequence_number.encode()
            self.socket.sendto(ack, address)
            # passa a esperar por outro pacote
            self.sequence_number = self.nott()
            print("Recebi direitinho")
            print("_____________\n\n")
        else:
            # recebeu um pacote duplicata
            ack = self.nott().encode()
            # reenvio ack do anterior, confirmando que ele já tinha sido recebido
            self.socket.sendto(ack, address)
            print("kitei")
            print("_____________\n\n")