from threading import Thread
from socket import AF_INET, SOCK_STREAM, socket

# Permitir import relativo
from sys import path
path.append('..')

from command import CommandResponseType, HelpCommand, ExitCommand


class ClientHandler(Thread):
    server_address: str

    def __init__(self, host: str, port: int):
        Thread.__init__(self)
        self.server_address = f'{host}:{port}'
        self.addr = (host, port)

    def get_available_commands(self):
        available_commands = [
            HelpCommand(),
            ExitCommand(),
        ]

        return available_commands

    def check_for_available_commands(self, command: str):
        available_commands = self.get_available_commands()

        for cmd in available_commands:
            if cmd.check(command):
                return cmd.run()

        return CommandResponseType.ERROR

    def run(self):
        with socket(AF_INET, SOCK_STREAM) as current_socket:
            current_socket.connect(self.addr)
            print(f'Iniciando conexão com {self.server_address}')

            while True:
                command = input('> ')

                code = self.check_for_available_commands(command)

                if code == CommandResponseType.ERROR:
                    print("Houve algum erro ao executar o comando, tente novamente!")
                    continue

                if code == CommandResponseType.STOP:
                    current_socket.close()
                    break

                current_socket.sendall(command.encode('utf8'))

        print(f'Finalizando conexão com {self.server_address}')
