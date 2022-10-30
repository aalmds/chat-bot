import time
from threading import Lock

# Classe de abstração para a máquina de estados do protocolo de transferência confiável do tranmissor.
class RdtSender:
    def __init__(self, socket, timeout=10):
        self.socket = socket
        self.sequence_number = '0'
        self.timeout = timeout

        # Definindo o estado inicial como o de espera por uma mensagem a ser transferida.
        self.waiting = True

        # Lock para ack.
        self.lock = Lock()
        self.ack = -1

    # Função que modifica o valor do ack.
    def set_ack(self, ack):
        self.ack = ack

    # Função que retorna o lock do ack.
    def get_lock(self):
        return self.lock

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
        
        # Capturando o tempo inicial.
        start_time = time.time()
        
        # Enviando pacote.
        self.socket.sendto(pkt.encode(), address)
        
        # Enquanto está no estado de espera pelo ack correto, continua retransmitindo o último pacote enviado após timeout.
        while not self.waiting:

            # Verificando se houve timeout.
            if time.time() - start_time > self.timeout:
                start_time = time.time()
                # Reenviando o pacote.
                self.socket.sendto(pkt.encode(), address)
                
            
            # Checando se o ack está correto.
            self.lock.acquire()
            if self.__check_ack():
                # Resetando ack.
                self.ack = -1
                # Atualizando número de sequências.
                self.__update_seqnum()
                # Modificando o estado para o de espera por chamada da aplicação para uma nova transmissão.
                self.waiting = True
            self.lock.release()

    # Função que retorna se o estado atual do transmissor permite transmissão de uma nova mensagem ou ainda está em espera do ack.
    def is_waiting_call(self):
        return self.waiting
