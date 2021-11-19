from threading import Thread
from socket import socket
from typing import Union
from json import dumps
from sys import path
path.append('..')
from command import CommandResponseType, get_server_commands

# from models import User


class ServerHandler(Thread):
    conn: socket
    client_address: str

    def __init__(self, conn: socket, addr: Union[str, int]):
        Thread.__init__(self)
        self.conn = conn
        self.client_address = f'{addr[0]}:{addr[1]}'
    
    def check_for_available_commands(self, command: str):
        available_commands = get_server_commands()        

        for cmd in available_commands:
            if cmd.check(command):
                return cmd.run()
        
        return CommandResponseType.ERROR
    
    def parse_response_code_as_json(self, code: CommandResponseType):
        response_object = {
            "code": code.__str__()
        }
        print(f"{response_object=}")

        return dumps(response_object).encode('utf8')

    def run(self):
        print(f'Iniciando conexão com {self.client_address}')

        with self.conn:
            while True:
                print(f'Aguardando comando de {self.client_address}')
                data = self.conn.recv(1024)

                if not data:
                    break

                command = data.decode('utf8')
                print("server - recebi", command)
                code = self.check_for_available_commands(command)
                response = self.parse_response_code_as_json(code)
                self.conn.sendall(response)

        print(f'Finalizando conexão com {self.client_address}')

