from typing import Dict, List
from json import dumps, loads
from os import system

from command_response_type import CommandResponseType
from models import User


class Command:
    name: str
    command_line: str

    def check(self, command_line: str):
        self.command_line = command_line

        return command_line.startswith(self.name)

    def get_args(self):
        if not self.command_line:
            return []

        return self.command_line.strip().split(" ")[1:]

    def run(self):
        return CommandResponseType.OK


class HelpCommand(Command):
    name = "help"

    def get_help_text(self):
        help_text_lines = [
            "Lista de comandos:",
            "- Mostrar comandos disponíveis:",
            "$ help\n",
            "- Sair da aplicação:",
            "$ exit\n",
            "- Criar um novo usuário no servidor:",
            "$ user create <nome do usuário> <email> <senha>\n",
            "- Listar todos usuários:",
            "$ user list all\n",
            "- Remover usuário:",
            "$ user remove <email ou ID>\n",
            "- Criar nova regra de firewall:",
            "$ rule add <ip address> <action>, onde action deve ser ACCEPT ou DENY\n",
            "- Listar regras do firewall:",
            "$ rule list all\n",
            "- Remover regras do firewall:",
            "$ rule remove <ID>\n",
            "- Aplicar regras do firewall",
            "$ firewall start\n",
            "- Remover regras do firewall",
            "$ firewall stop"
        ]

        return '\n'.join(help_text_lines)

    def run(self):
        content = self.get_help_text()
        print(content)

        return CommandResponseType.OK


class ClearCommand(Command):
    name = "clear"

    def run(self):
        system('clear')
        return CommandResponseType.OK


class ExitCommand(Command):
    name = "exit"

    def run(self):
        return CommandResponseType.STOP


class UserCommand(Command):
    name = "user"
    database_name = 'database.json'

    def get_database_content(self):
        with open(file=self.database_name, mode='r') as file:
            content = '\n'.join(file.readlines())
            return content

    def save_dict_to_database(self, database_dict):
        with open(file=self.database_name, mode='w') as file:
            content_json = dumps(database_dict, indent=2)
            file.write(content_json)

    def add_user_to_database(self, user: User):
        db = {}

        content = self.get_database_content()
        db.update(loads(content))
        db['users'].update({user.id: user.get()})

        self.save_dict_to_database(db)

        code = CommandResponseType.OK
        message = 'Usuário criado com sucesso!'

        return (code, message)

    def parse_users_list_as_string(self, users: Dict[str, str]):
        return 'Lista de usuários cadastrados:\n' + '\n'.join(
            map(
                lambda x: f'\
                    ID: {x}\n\
                    Nome: {users[x]["name"]}\n\
                    Email: {users[x]["email"]}\n',
                users
            ))

    def get_users_from_database(self):
        content = self.get_database_content()
        users = loads(content).get('users')

        if not users:
            return None

        return self.parse_users_list_as_string(users)

    def create_user(self, args: List[str]):
        if len(args) < 3:
            code = CommandResponseType.ERROR
            message = "Número de argumentos inválido!"
            return (code, message)

        password = args.pop()
        email = args.pop()
        name = ' '.join(args)
        user = User(name, email, password)

        return self.add_user_to_database(user)

    def list_users(self, args: List[str]):
        code = CommandResponseType.ERROR
        if len(args) != 1:
            message = "Número de argumentos inválido!"
            return (code, message)

        flag = args.pop()
        if flag != 'all':
            message = "Sinalizador inválido!"
            return (code, message)

        users = self.get_users_from_database()
        if users is None:
            message = "Não foi possível obter usuários do banco de dados!"
            return (code, message)

        code = CommandResponseType.OK
        return (code, users)

    def remove_user(self, args: List[str]):
        code = CommandResponseType.ERROR
        if len(args) != 1:
            message = "Número de argumentos inválido!"
            return (code, message)

        email_or_id = args.pop()

        content = self.get_database_content()
        database = loads(content)
        user_list = database.get("users")

        for user_id in user_list:
            user = user_list[user_id]
            if email_or_id in [user_id, user.get("email")]:
                user_list.pop(user_id)

                database['users'] = user_list

                self.save_dict_to_database(database)

                code = CommandResponseType.OK
                message = "Usuário removido com sucesso!"
                return (code, message)

        message = "Usuário não encontrado!"
        return (code, message)

    def run(self):
        code = CommandResponseType.ERROR

        available_actions = {
            'create': self.create_user,
            'list': self.list_users,
            'remove': self.remove_user,
        }

        args = self.get_args()
        if not (args and len(args) >= 1):
            message = "Não há argumentos suficientes!"
            return (code, message)

        command_action = args.pop(0)

        if command_action not in available_actions:
            message = "Operação não identificada!"
            return (code, message)

        selected_action = available_actions[command_action]
        return selected_action(args)


def get_client_commands():
    return [
        ClearCommand(),
        HelpCommand(),
        ExitCommand()
    ]


def get_server_commands():
    return [
        UserCommand()
    ]
