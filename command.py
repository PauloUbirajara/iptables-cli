from typing import List

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

    def create_user(self, args: List[str]):
        print("Criar usuário", args)
        return CommandResponseType.OK

    def list_users(self, args: List[str]):
        print("Mostrar lista de usuários", args)
        return CommandResponseType.OK

    def remove_user(self, args: List[str]):
        print("Deletar usuário", args)
        return CommandResponseType.OK

    def run(self):
        available_actions = {
            'create': self.create_user,
            'list': self.list_users,
            'remove': self.remove_user,
        }

        args = self.get_args()
        if not args:
            return CommandResponseType.ERROR

        command_action = args[0]

        if command_action not in available_actions:
            return CommandResponseType.ERROR

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
