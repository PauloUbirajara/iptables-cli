from bcrypt import gensalt, hashpw, checkpw
from uuid import uuid1


class User:
    id: str
    name: str
    email: str
    password: bytes

    def __init__(self, name: str, email: str, password: str):
        self.id = str(uuid1())
        self.name = name
        self.email = email
        self.password = self.encrypt_password(password)

    def encrypt_password(self, password: str):
        return hashpw(password.encode('utf8'), gensalt())

    def check_password(self, other_pwd: str):
        return checkpw(other_pwd.encode('utf8'), self.password)

    def get(self):
        return {
            'name': self.name,
            'email': self.email,
            'password': self.password.decode('utf8')
        }
