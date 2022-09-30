from Utils import _BUFFER_SIZE

# Classe de abstração para a máquina de estados do protocolo de transferência confiável do receptor.
class RdtReceiver:
    def __init__(self, socket):
        self.sequence_number = '0'
        self.socket = socket

    # Função que verifica se o número de sequência do pacote recebido é igual ao esperado.
    def __check_pkt(self, seqnum):
        return seqnum == self.sequence_number

    # Função auxiliar para atualização do número de sequência e do ack.
    def __nott(self):
        return '0' if self.sequence_number == '1' else '1' 

    # Função referente ao recebimento da mensagem por um canal confiável.
    def receive(self):
        message, clientAddress = self.socket.recvfrom(_BUFFER_SIZE)
        seqnum, data = message.decode().split(',')

        # Verificando se o pacote recebido é igual ao esperado e não uma duplicata.
        if self.__check_pkt(seqnum):
            # Criando e enviando o reconhecimento do pacote atual.
            ack = self.sequence_number.encode()
            print(f"Package is correct, sending ack {ack.decode()}!\n\n")
            self.socket.sendto(ack, clientAddress)

            # Atualizando o número de sequência esperado.
            self.sequence_number = self.__nott()
        else:
            # Criando e reenviando o ack do pacote anterior já que houve identificação de duplicata.
            ack = self.__nott().encode()
            print(f"Duplicate detected, resending ack {ack.decode()}!\n\n")
            self.socket.sendto(ack, clientAddress)
            