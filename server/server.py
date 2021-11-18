from socket import AF_INET, SOCK_STREAM, socket
from threading import Thread
from typing import Union

from server_handler import ServerHandler


class Server(Thread):
    addr: Union[str, int]

    def __init__(self, host: str, port: int):
        Thread.__init__(self)
        self.addr = (host, port)

    def run(self):
        with socket(AF_INET, SOCK_STREAM) as s:
            s.bind(self.addr)
            s.listen(1)

            while True:
                conn, addr = s.accept()

                handler = ServerHandler(conn, addr)
                handler.start()
