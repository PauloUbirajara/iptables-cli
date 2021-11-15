from socket import AF_INET, SOCK_STREAM, socket
from threading import Thread

from handler import Handler


class Client(Thread):
    host: str
    port: int

    def __init__(self, host, port):
        Thread.__init__(self)
        self.host = host
        self.port = port

    def server_address(self):
        return f'{self.host}:{self.port}'

    def run(self):
        with socket(AF_INET, SOCK_STREAM) as current_socket:

            handler = Handler(self.host, self.port, current_socket)
            current_socket.connect((self.host, self.port))

            handler.start()
