from client import Client

if __name__ == '__main__':
    print('Inicializando o client...')

    client = Client('localhost', 5000)
    client.start()
