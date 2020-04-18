import socket
import sys
import threading
import os
import protocolo
from protocolo import Mensagem

class Cliente:

    def __init__(self, host = 'localhost', port = 50006):
        self.host = host
        self.port = port

    def enviarMensagem(self):
        try:
            while True:
                mensagem = input()
                mensagemChat = Mensagem(mensagem)
                self.s.send(mensagemChat.get_bytes())
                isSaida = mensagem.split()
                if not isSaida:
                    continue
                if isSaida[0]  == '\close':
                    self.s.close()
                    os._exit(1)
        except:
            mensagem = '\close'
            self.s.send(mensagem.encode('utf-8'))
            self.s.close()
            os._exit(1)

    def receberMensagem(self):
        while True:
            mensagem = self.s.recv(4096)
            mensagemChat = Mensagem.from_buffer(mensagem)
            if mensagem == '\SERVIDOR_OFF':
                print('Encerrando conexão')
                self.s.close()
                os._exit(1)
            print(mensagemChat.msg)

    def main(self):
        self.criarConexao()
        thread = threading.Thread(target= self.receberMensagem)
        thread.start()
        self.enviarMensagem()

    def criarConexao(self):
        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except:
            print('Erro ao tentar criar o socket')
            os._exit(1)
        conexaoDestino = (self.host, self.port)
        try:
            self.s.connect(conexaoDestino)
        except:
            print('servidor sem conexão')
            sys.exit()

if __name__ == "__main__":
	cliente = Cliente()
	cliente.main()