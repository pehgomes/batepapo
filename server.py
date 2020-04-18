import socket
import sys
import threading
import os
import time
from protocolo import Mensagem, Nickname

class Servidor:
    def __init__(self, host = 'localhost', port = 50006):
        self.finaliza = '\SERVIDOR_OFF'

        self.host = host
        self.port = port
        self.palavrasChave = ['\close', '\\nickname']
        self.clientes = {}

    def main(self):
        try:
            self.criarConexao()
            self.receberConexaoClientes()
        except:
            os._exit(1)

    def criarConexao(self):
        destino = (self.host, self.port)
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.s.bind(destino)
            self.s.listen(5)
        except:
            print('Nao foi possivel vincular')
            os._exit(1)

    def encerrarConexao(self):
        self.s.close()

    def encerrarDemaisConexoes(self):
        for apelido, conn in list(self.clientes.items()):
            con = conn
            con.close()

    def verificaApelido(self, novoApelido):
        if novoApelido in self.palavrasChave:
            return True
        return novoApelido in self.clientes

    def verificarComandoOuMensagem(self, conexao, remetente, pacoteMensagem):
        mensagem = pacoteMensagem.msg
        isComando = mensagem.strip()
        isComando = list(isComando)
        if isComando[0] == '\\':
            isComando = mensagem.split()
            if (isComando[0] == '\close'):
                print('{} saiu do bate-papo.'.format(remetente))
                msgSaiu = '{} saiu do bate-papo.'.format(remetente)
                mensagePacote = Mensagem(msgSaiu)
                self.enviarMensagemPublica(remetente, mensagePacote)
                self.finalizarConexaoCliente(remetente)
            if (isComando[0] == '\\nickname'):
                self.trocarNickname(conexao, remetente)
        else:
            self.enviarMensagemPublica(remetente, pacoteMensagem)

    def finalizarConexaoCliente(self, apelido, banido = 0):
        conexao = self.clientes.get(apelido)
        del self.clientes[apelido]
        mensagem = apelido + ' saiu do grupo'
        self.enviarMensagemPublica(apelido, mensagem, 1)
        conexao.close()

    def trocarNickname(self, conexao, apelido):
        try:
            msg = 'Para qual nickname vc deseja trocar ?'
            conexao.send(Mensagem(msg).get_bytes())
            nickinBytes = conexao.recv(4096)
            mensagemChatNickname = Nickname.from_buffer(nickinBytes)
            nick = mensagemChatNickname.nickname
            nickexiste = self.verificaApelido(nick)

            if nickexiste:
                conexao.send(Mensagem('O nick ja esta sendo utilizado').get_bytes())
                return
            del self.clientes[apelido]
            self.clientes[nick] = conexao
            if nick:
                msg = 'Nickname atualizado para {}'.format(nick)
                conexao.send(Mensagem(msg).get_bytes())
        except:
            pass

    def enviarMensagemPublica(self, remetente, pacoteMensagem, flag = 0):
        mensagem = pacoteMensagem.msg
        def enviarMensagemTodos():
            for apelido, con in list(self.clientes.items()):
                conexao = con
                if apelido != remetente:
                    self.enviarMensagem(conexao, apelido, mensagem)
        if not self.clientes:
            return
        if flag:
            if not remetente:
                enviarMensagemTodos()
                self.encerrarDemaisConexoes()
            else:
                mensagem = remetente + '' + mensagem
        else:
            mensagem = '< ' +str(pacoteMensagem.version) + ' ' +str(pacoteMensagem.length) + ' ' +str(pacoteMensagem.type)+' ' + remetente +' > : ' + mensagem
            con = self.clientes.get(remetente)
        enviarMensagemTodos()

    def enviarMensagem(self, conexao, apelido, mensagem):
        try:
            pacoteMensagem = Mensagem(mensagem)
            conexao.send(pacoteMensagem.get_bytes())
        except:
            pass

    def receberMensagem(self, apelido, conexao):
        while True:
            try:
                mensagemEncapsulada = conexao.recv(4096)
                pacoteMensagem = Mensagem.from_buffer(mensagemEncapsulada)
                self.verificarComandoOuMensagem(conexao, apelido, pacoteMensagem)
            except:
                break

    def receberConexaoClientes(self):
        while True:
            conexao, endereco = self.s.accept()
            thread = threading.Thread(target = self.controlarConexao, args= (conexao,))
            thread.start()

    def controlarConexao(self, conexao):
        conexao.send(Mensagem('Bem vindo ao bate papo ! Como quer ser chamado ?').get_bytes())
        mensagemInicialEmpacotada = conexao.recv(4096)
        protocoloMensagem = Mensagem.from_buffer(mensagemInicialEmpacotada)
        apelido = protocoloMensagem.msg
        existeApelido = self.verificaApelido(apelido)

        if mensagemInicialEmpacotada:
            msg = "Seja bem-vindo {} !".format(apelido)
            conexao.send(Mensagem(msg).get_bytes())

        if existeApelido:
            conexao.send(Mensagem('Desculpe, este mensagemInicialEmpacotada ja existe').get_bytes())

        print("{} acabou de entrar no batepapo".format(apelido))
        self.clientes[apelido] = conexao
        pacoteMensagem = Mensagem(' entrou no grupo')
        self.enviarMensagemPublica(apelido, pacoteMensagem, 1)
        self.receberMensagem(apelido, conexao)

if __name__ == "__main__":
    server = Servidor()
    server.main()