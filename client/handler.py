# Permitir import relativo
from socket import socket
from sys import path
path.append('..')

from command import CommandResponseType, HelpCommand, ExitCommand


class Handler:
    host: str
    port: int
    socket: socket
    server_address: str

    def __init__(self, host: str, port: int, socket: socket):
        self.host = host
        self.port = port
        self.socket = socket
        self.server_address = f'{self.host}:{self.port}'

    def get_available_commands(self):
        available_commands = [
            HelpCommand(self.socket),
            ExitCommand(self.socket),
        ]

        return available_commands

    def check_for_available_commands(self, command: str):
        available_commands = self.get_available_commands()

        for cmd in available_commands:
            if cmd.check(command):
                return cmd.run()

        return CommandResponseType.ERROR

    def start(self):
        print(f'Realizando conexão com {self.server_address}')

        while True:
            command = input('> ')

            code = self.check_for_available_commands(command)
            if code == CommandResponseType.ERROR:
                print("Houve algum erro ao executar o comando, tente novamente!")

            if code == CommandResponseType.STOP:
                break

        print(f'Finalizando conexão com {self.server_address}')
