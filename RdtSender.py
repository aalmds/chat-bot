import time

class RdtSender:
    def __init__(self, socket, timeout=10):
        self.socket = socket
        self.sequence_number = '0'
        self.timeout = timeout
        # Definindo o estado inicial como o de espera por uma mensagem a ser transferida.
        self.waiting = True
        self.ack = -1

    def set_ack(self, ack):
        self.ack = ack

    # Função que verifica se o ack recebido é referente ao pacote que foi enviado por último.
    def __check_ack(self):
        return self.sequence_number == self.ack

    # Função que atualiza o número de sequência.
    def __update_seqnum(self):
        self.sequence_number = '0' if self.sequence_number == '1' else '1'

    # Função referente ao envio da mensagem por um canal confiável.
    def send(self, chunk, address):
        self.waiting = False

        # Criando o pacote com número de sequência e dado.
        pkt = self.sequence_number + "%&%" + chunk
        start_time = time.time()

        self.socket.sendto(pkt.encode(), address)
        # Enquanto está no estado de espera pelo ack correto, continua retransmitindo o último pacote enviado após timeout.
        while not self.waiting:
            if time.time() - start_time > self.timeout:
                self.socket.sendto(pkt.encode(), address)
                start_time = time.time()
                continue

            if self.__check_ack():
                self.ack = -1
                self.__update_seqnum()
                self.waiting = True
    

    # Função que retorna se o estado atual do transmissor permite transmissão de uma nova mensagem ou ainda está em espera do ack.
    def is_waiting_call(self):
        return self.waiting
