from threading import Thread
from socket import socket
from typing import Union
from json import dumps
from sys import path
path.append('..')
from command_response_type import CommandResponseType
from command import get_server_commands


class ServerHandler(Thread):
    conn: socket
    client_address: str

    def __init__(self, conn: socket, addr: Union[str, int]):
        Thread.__init__(self)
        self.conn = conn
        self.client_address = f'{addr[0]}:{addr[1]}'

    def parse_response_code_as_json(self, code: CommandResponseType, message: str):
        response_object = {
            "message": message,
            "code": code.__str__()
        }
        print(f"{response_object=}")

        return dumps(response_object).encode('utf8')

    def check_for_available_commands(self, command: str):
        available_commands = get_server_commands()

        for cmd in available_commands:
            if cmd.check(command):
                return cmd.run()

        return (CommandResponseType.ERROR, "Comando inválido!")

    def run(self):
        print(f'[+] Novo client: {self.client_address}')

        with self.conn:
            while True:
                print(f'Aguardando comando de {self.client_address}')
                data = self.conn.recv(1024)

                if not data:
                    break

                command = data.decode('utf8')
                print("server - recebi", command)
                code, message = self.check_for_available_commands(command)
                response = self.parse_response_code_as_json(code, message)
                self.conn.sendall(response)

        print(f'[-] Client desconectou: {self.client_address}')
