class CommandResponseType:
    OK = 0
    ERROR = 1
    STOP = 2


class Command:
    name: str

    def check(self, command):
        return command == self.name

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


class ExitCommand(Command):
    name = "exit"

    def run(self):
        return CommandResponseType.STOP
