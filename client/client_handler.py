from threading import Thread
from socket import AF_INET, SOCK_STREAM, socket, SocketType
from sys import path
path.append('..')

from command import CommandResponseType, get_available_commands


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
        
        #! Verificar a estrutura tipo HTTP (OK, ERROR)
        return CommandResponseType.OK

    def check_for_available_commands(self, command: str):
        available_commands = get_available_commands()
        #@ Ao invés de realizar duas verificações, enviar diretamente o comando para o servidor, lá ele verifica e retorna de acordo (ok, error, stop)
        #@ Ao invés de percorrer a lista de comandos retornados, transformar em dicionários e verificar se começa com alguem da lista de chaves

        for cmd in available_commands:
            if cmd.check(command):
                self.socket.sendall(command.encode('utf8'))
                return self.parse_server_response()

        return CommandResponseType.ERROR

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
