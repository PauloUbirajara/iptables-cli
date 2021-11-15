import json

from models import User
from threading import Thread


class Handler(Thread):

    def __init__(self, conn, addr):
        Thread.__init__(self)
        self.conn = conn
        self.addr = addr

    def run(self):
        with self.conn:
            client_address = f'{self.addr[0]}:{self.addr[1]}'

            while True:
                print(f'Aguardando comando de {client_address}')
                data = self.conn.recv(1024)
                if not data:
                    break

                request = data.decode('utf8')
                print('recebi', request)

            print(f'Finalizando conexão com {client_address}')

            # if request['action'] == 'create_user':
            #   file = open(file='database.json', mode='r')
            #   content = file.read()
            #   file.close()
            #   db = json.loads(content)

            #   user = User(request['data']['name'], request['data']['email'], request['data']['password'])

            #   db['users'].append(user.map())

            #   content = json.dumps(db)
            #   file = open(file='database.json', mode='w')
            #   file.write(content)
            #   file.close()

            # else:
            #   self.conn.sendall("Invalid command".encode('utf8'))
