from threading import Thread

from client_handler import ClientHandler


class Client(Thread):
    host: str
    port: int

    def __init__(self, host: str, port: int):
        Thread.__init__(self)
        self.host = host
        self.port = port

    def run(self):
        addr = (self.host, self.port)

        handler = ClientHandler(*addr)
        handler.start()
