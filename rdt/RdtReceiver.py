from utils import _BUFFER_SIZE

# Classe de abstração para a máquina de estados do protocolo de transferência confiável do receptor.
class RdtReceiver:
    def __init__(self, socket, seqnum='0'):
        self.sequence_number = seqnum
        self.socket = socket

    # Função que verifica se o número de sequência do pacote recebido é igual ao esperado.
    def __check_pkt(self, seqnum):
        return seqnum == self.sequence_number

    # Função auxiliar para atualização do número de sequência e do ack.
    def __nott(self):
        return '0' if self.sequence_number == '1' else '1'

    # Função referente ao recebimento da mensagem por um canal confiável.
    def receive(self, address, seqnum, message):
        # Enquanto o pacote recebido não é o esperado, continua tentando receber o com número de sequência correto.
        while not self.__check_pkt(seqnum):
            # Criando e reenviando o ack do pacote anterior já que houve identificação de duplicata.
            ack = self.__nott().encode()
            self.socket.sendto(ack, address)

            message, _ = self.socket.recvfrom(_BUFFER_SIZE)
            seqnum, message = message.decode().split('%&%')

        # Enviando o ack referente ao pacote que foi recebido corretamente.
        ack = self.sequence_number.encode()
        self.socket.sendto(ack, address)

        # Atualizando o número de sequência esperado.
        self.sequence_number = self.__nott()
        return message


