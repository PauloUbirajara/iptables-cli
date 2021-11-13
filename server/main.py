from server import Server

if __name__ == '__main__':

  print('Inicializando o server...')

  server = Server('localhost', 50005)
  server.start()

