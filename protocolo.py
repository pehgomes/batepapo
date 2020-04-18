import struct
from abc import ABC, abstractmethod

# Definições do protocolo
PROTOCOL_VERSION = 1
PROTOCOL_HEADER_FORMAT = '!BHB'
PROTOCOL_HEADER_LENGTH = struct.calcsize(PROTOCOL_HEADER_FORMAT)

# Tipos de Mensagem
NICKNAME_MESSAGE_TYPE = 1
CHAT_MESSAGE_TYPE = 2
CLIENT_CONNECTION_TYPE = 3
CLIENT_CLOSE_CONN_TYPE = 4

class ProtocoloBase(ABC):

    def __init__(self):
        self.version = 0
        self.length = 0
        self.type = 0

    @abstractmethod
    def get_bytes(self):
        pass

    @staticmethod
    @abstractmethod
    def from_buffer(msg):
        pass

class Nickname(ProtocoloBase):

    def __init__(self, nickname):
        super().__init__()
        self.version = PROTOCOL_VERSION
        self.type = NICKNAME_MESSAGE_TYPE
        self.length = PROTOCOL_HEADER_LENGTH + len(nickname.encode('utf8'))
        self.nickname = nickname

    def get_bytes(self):
        return struct.pack(f'{PROTOCOL_HEADER_FORMAT}{self.length - PROTOCOL_HEADER_LENGTH}s', self.version, self.length, self.type, self.nickname.encode('utf8'))

    @staticmethod
    def from_buffer(msg):
        data = struct.unpack(f'{PROTOCOL_HEADER_FORMAT}{len(msg) - PROTOCOL_HEADER_LENGTH}s', msg)
        return Nickname(str(data[3],'utf8'))


class Mensagem(ProtocoloBase):

    def __init__(self, msg):
        super().__init__()
        self.version = PROTOCOL_VERSION
        self.type = CHAT_MESSAGE_TYPE
        self.length = PROTOCOL_HEADER_LENGTH + len(msg.encode('utf8'))
        self.msg = msg

    def get_bytes(self):
        return struct.pack(f'{PROTOCOL_HEADER_FORMAT}{self.length - PROTOCOL_HEADER_LENGTH}s', self.version,
                           self.length, self.type, self.msg.encode('utf8'))

    @staticmethod
    def from_buffer(msg):
        data = struct.unpack(f'{PROTOCOL_HEADER_FORMAT}{len(msg) - PROTOCOL_HEADER_LENGTH}s', msg)
        return Mensagem(str(data[3], 'utf8'))

