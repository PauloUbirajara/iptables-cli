from threading import Thread
from socket import socket
from typing import Union
from sys import path
path.append('..')
from command import CommandResponseType, get_available_commands

# from models import User


class ServerHandler(Thread):
    conn: socket
    client_address: str

    def __init__(self, conn: socket, addr: Union[str, int]):
        Thread.__init__(self)
        self.conn = conn
        self.client_address = f'{addr[0]}:{addr[1]}'

    def run(self):
        print(f'Iniciando conexão com {self.client_address}')

        with self.conn:
            while True:
                print(f'Aguardando comando de {self.client_address}')
                data = self.conn.recv(1024)

                if not data:
                    break

                print('recebi!', data)

        print(f'Finalizando conexão com {self.client_address}')

