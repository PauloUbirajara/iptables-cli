from json import loads
from socket import AF_INET, SOCK_STREAM, socket, SocketType
from threading import Thread
from sys import path
path.append('..')
from command_response_type import CommandResponseType
from command import get_client_commands


class ClientHandler(Thread):
    server_address: str
    socket: SocketType

    def __init__(self, host: str, port: int):
        Thread.__init__(self)
        self.server_address = f'{host}:{port}'
        self.addr = (host, port)

    def parse_server_response(self):
        data = self.socket.recv(1024)

        if not data:
            return CommandResponseType.ERROR

        response = loads(data.decode('utf8'))

        code_labels = {
            str(CommandResponseType.OK): "SUCESSO",
            str(CommandResponseType.ERROR): "FALHA",
        }

        code = response['code']
        label = code_labels[code]

        message = response['message']

        print(f'{label}\n{"="*15}\n{message}')
        return code

    def check_for_available_commands(self, command: str):
        available_commands = get_client_commands()

        for cmd in available_commands:
            if cmd.check(command):
                return cmd.run()

        self.socket.sendall(command.encode('utf8'))
        return self.parse_server_response()

    def run(self):
        with socket(AF_INET, SOCK_STREAM) as current_socket:
            self.socket = current_socket

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

        print(f'Finalizando conexão com {self.server_address}')
