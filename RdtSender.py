import socket
from Utils import _BUFFER_SIZE

# Classe de abstração para a máquina de estados do protocolo de transferência confiável do transmissor.


class RdtSender:
    def __init__(self, socket):
        self.socket = socket
        self.sequence_number = '0'
        # Definindo o estado inicial como o de espera por uma mensagem a ser transferida.
        self.waiting = True

    # Função que verifica se o ack recebido é referente ao pacote que foi enviado por último.
    def __check_ack(self, ack):
        return ack == self.sequence_number

    # Função que atualiza o número de sequência.
    def __update_seqnum(self):
        self.sequence_number = '0' if self.sequence_number == '1' else '1'

    # Função referente ao envio da mensagem por um canal confiável.
    def send(self, chunk, address):
        self.waiting = False

        # Criando o pacote com número de sequência e dado.
        pkt = self.sequence_number + "%&%" + chunk

        # Enquanto está no estado de espera pelo ack correto, continua retransmitindo o último pacote enviado após timeout.
        while not self.waiting:
            print(
                f"Sending package with: ({self.sequence_number}, \"{chunk}\")")
            self.socket.sendto(pkt.encode(), address)

            # Ligando o temporizador
            self.socket.settimeout(0.5)

            try:
                ack, address = self.socket.recvfrom(_BUFFER_SIZE)
            except socket.timeout:
                # Detectando timeout.
                print("Timeout!\n\n")
                continue

            # Verificando se o ack recebido é correto.
            if self.__check_ack(ack.decode()):
                print("The ack is correct!\n\n")

                # Desligando o temporizador
                self.socket.settimeout(None)
                # Atualizando o número de sequência.
                self.__update_seqnum()

                # Voltando para o estado de espera pela transmissão de uma nova mensagem.
                self.waiting = True

    # Função que retorna se o estado atual do transmissor permite transmissão de uma nova mensagem ou ainda está em espera do ack.
    def is_waiting_call(self):
        return self.waiting
