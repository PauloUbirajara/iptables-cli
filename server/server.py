from socket import AF_INET, SOCK_STREAM, socket
from threading import Thread
from typing import Union
from os.path import isfile
from json import dumps

from server_handler import ServerHandler


class Server(Thread):
    addr: Union[str, int]
    database_name = 'database.json'

    def __init__(self, host: str, port: int):
        Thread.__init__(self)
        self.addr = (host, port)
        self.create_database_if_not_exists()

    def create_database_if_not_exists(self):
        if not isfile(self.database_name):
            default_database = {'users': {}, 'rules': {}}

            with open(file=self.database_name, mode='w') as file:
                file.write(dumps(default_database))

    def run(self):
        with socket(AF_INET, SOCK_STREAM) as s:
            s.bind(self.addr)
            s.listen(1)

            while True:
                conn, addr = s.accept()

                handler = ServerHandler(conn, addr)
                handler.start()
