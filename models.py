from bcrypt import gensalt, hashpw, checkpw
from uuid import uuid1


class User:
    id: str
    name: str
    email: str
    password: bytes

    def __init__(self, name: str='', email: str='', password: str=''):
        self.id = str(uuid1())
        self.name = name
        self.email = email
        self.password = self.encrypt_password(password)
    
    @staticmethod
    def new_from_dict(id, user_dict):
        result = User()

        result.id = id
        result.email = user_dict['email']
        result.password = user_dict['password']
        result.name = user_dict['name']

        return result

    def encrypt_password(self, password: str):
        return hashpw(password.encode('utf8'), gensalt())

    @staticmethod
    def check_password(password: str, hashed_password: str):
        validation = checkpw(
            password.encode('utf8'),
            hashed_password.encode('utf8')
        )

        return validation

    def get(self):
        return {
            'name': self.name,
            'email': self.email,
            'password': self.password.decode('utf8')
        }


class Rule:
    id: str
    ip: str
    action: str

    def __init__(self, user_id: str, ip: str, action: str):
        self.id = str(uuid1())
        self.user_id = user_id
        self.ip = ip
        self.action = action

    def get(self):
        return {
            'user_id': self.user_id,
            'ip': self.ip,
            'action': self.action,
        }
