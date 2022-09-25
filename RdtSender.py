from Utils import _BUFFER_SIZE

class RdtSender:
    def __init__(self, socket):
        self.socket = socket
        self.ack = '0'
        self.sequence_number = '0'
        self.timer = 5
        
    def __check_ack(self, ack):
        return ack == self.ack

    def __reset_timer(self):
        self.timer = 5

    def __nott(self, msg):
        return '0' if msg == '1' else '1' 
        
    def send(self, chunk, address):
        pkt = self.sequence_number + "," + chunk
        print("Message:", pkt)
        self.socket.sendto(pkt.encode(), address)

        # liga o temporizador
        while self.timer:
            self.timer -= 1
            print(self.timer)
            # espera pelo ack
            ack, address = self.socket.recvfrom(_BUFFER_SIZE)
            if self.__check_ack(ack.decode()):
                print("Ack recebido:", ack.decode())
                print("\n_____________\n\n")
                self.__reset_timer()
                # ira mandar outro pacote
                self.sequence_number = self.__nott(self.sequence_number)
                # ira esperar ack de outro pacote
                self.ack = self.__nott(self.ack)
                return

        # deu timeout
        print("deu timeout!!!")
        self.__reset_timer()
        self.rdt_sender(chunk)