from types import FunctionType
from typing import Dict, List
from json import dumps, loads
from os import system

from command_response_type import CommandResponseType
from models import User, Rule


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


class DatabaseCommand(Command):
    database_name = 'database.json'
    available_actions: Dict[str, FunctionType]

    def get_database_content(self):
        '''
        Abre o arquivo de banco de dados e retorna uma string contendo o
        que foi salvo.
        '''

        with open(file=self.database_name, mode='r') as file:
            content = '\n'.join(file.readlines())
            return content

    def save_dict_to_database(self, database_dict):
        '''
        Salva um objeto representando o novo estado do banco de dados no
        arquivo .json.
        '''

        with open(file=self.database_name, mode='w') as file:
            content_json = dumps(database_dict, indent=2)
            file.write(content_json)

    def run(self):
        '''
        Método principal para realizar operações relacionadas ao banco de
        dados. (Usuário/Regras)
        '''

        code = CommandResponseType.ERROR

        args = self.get_args()
        if not (args and len(args) >= 1):
            message = "Não há argumentos suficientes!"
            return (code, message)

        command_action = args.pop(0)

        if command_action not in self.available_actions:
            message = "Operação não identificada!"
            return (code, message)

        selected_action = self.available_actions[command_action]
        return selected_action(args)


class UserCommand(DatabaseCommand):
    name = "user"

    def __init__(self):
        self.available_actions = {
            'create': self.create_user,
            'list': self.list_users,
            'remove': self.remove_user,
        }

    def add_user_to_database(self, user: User):
        '''
        Abre o arquivo .json de banco de dados e atualiza a seção de 'users'
        com o novo usuário.
        '''

        db = {}

        content = self.get_database_content()
        db.update(loads(content))
        db['users'].update({user.id: user.get()})

        self.save_dict_to_database(db)

        code = CommandResponseType.OK
        message = 'Usuário criado com sucesso!'

        return (code, message)

    def parse_user_list_as_string(self, users: Dict[str, str]):
        '''
        Retorna uma lista de usuários do banco de dados formatada para
        leitura pelo usuário.
        '''

        return 'Lista de usuários cadastrados:\n' + \
            '\n'.join(map(
                lambda x:
                f'ID: {x}\n' +
                f'Nome: {users[x]["name"]}\n' +
                f'Email: {users[x]["email"]}\n',
                users
            ))

    def get_users_from_database(self):
        '''
        Retorna usuários no banco de dados na seção 'users'.
        '''

        content = self.get_database_content()
        users = loads(content).get('users')

        if not users:
            return None

        return self.parse_user_list_as_string(users)

    def create_user(self, args: List[str]):
        '''
        Método principal chamado para adicionar um usuário no banco de dados.
        '''

        code = CommandResponseType.ERROR

        if len(args) < 3:
            message = "Número de argumentos inválido!"
            return (code, message)

        password = args.pop()
        email = args.pop()
        name = ' '.join(args)
        user = User(name, email, password)

        return self.add_user_to_database(user)

    def list_users(self, args: List[str]):
        '''
        Método principal chamado para listar usuários no banco de dados.
        '''

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
        '''
        Método principal chamado para remover um usuário do banco de dados.
        '''

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


class RuleCommand(DatabaseCommand):
    name = "rule"

    def __init__(self):
        self.available_actions = {
            'add': self.add_rule,
            'list': self.list_rules,
            'remove': self.remove_rule,
        }

    def add_rule_to_database(self, rule: Rule):
        '''
        Abre o arquivo .json de banco de dados e atualiza a seção de 'rules'
        com a nova regra.
        '''

        db = {}

        content = self.get_database_content()
        db.update(loads(content))
        db['rules'].update({rule.id: rule.get()})

        self.save_dict_to_database(db)

        code = CommandResponseType.OK
        message = 'Regra criada com sucesso!'

        return (code, message)

    def parse_rule_list_as_string(self, rules: Dict[str, str]):
        '''
        Retorna uma lista de regras do banco de dados formatada para
        leitura pelo usuário.
        '''

        return 'Lista de regras cadastradas:\n' + \
            '\n'.join(map(
                lambda x:
                f'ID: {x}\n' +
                f'Endereço IP: {rules[x]["ip"]}\n' +
                f'Ação: {rules[x]["action"]}\n',
                rules
            ))

    def get_rules_from_database(self):
        '''
        Retorna as regras do banco de dados na seção 'rules'.
        '''

        content = self.get_database_content()
        rules = loads(content).get('rules')

        if not rules:
            return None

        return self.parse_rule_list_as_string(rules)

    def add_rule(self, args: List[str]):
        '''
        Método principal chamado para adicionar uma regra no banco de dados.
        '''

        code = CommandResponseType.ERROR

        if len(args) != 2:
            message = "Número de argumentos inválido!"
            return (code, message)

        ip, action = args
        available_actions = ["ACCEPT", "DENY"]

        if action not in available_actions:
            message = "Ação inválida!"
            return (code, message)

        rule = Rule(ip, action)

        return self.add_rule_to_database(rule)

    def list_rules(self, args: List[str]):
        '''
        Método principal chamado para listar regras no banco de dados.
        '''

        code = CommandResponseType.ERROR
        if len(args) != 1:
            message = "Número de argumentos inválido!"
            return (code, message)

        flag = args.pop()
        if flag != 'all':
            message = "Sinalizador inválido!"
            return (code, message)

        rules = self.get_rules_from_database()
        if rules is None:
            message = "Não foi possível obter regras do banco de dados!"
            return (code, message)

        code = CommandResponseType.OK
        return (code, rules)

    def remove_rule(self, args: List[str]):
        '''
        Método principal chamado para remover uma regra do banco de dados.
        '''

        code = CommandResponseType.ERROR

        if len(args) != 1:
            message = "Número de argumentos inválido!"
            return (code, message)

        address_or_id = args.pop()

        content = self.get_database_content()
        database = loads(content)
        rule_list = database.get("rules")

        for rule_id in rule_list:
            rule = rule_list[rule_id]
            if address_or_id in [rule_id, rule.get("ip")]:
                rule_list.pop(rule_id)

                database['rules'] = rule_list

                self.save_dict_to_database(database)

                code = CommandResponseType.OK
                message = "Regra removida com sucesso!"
                return (code, message)

        message = "Regra não encontrada!"
        return (code, message)


class FirewallCommand(Command):
    name = "firewall"

    def start(self):
        '''
        Método principal para permitir compartilhamento de pacotes e
        executar regras salvas no banco de dados no iptables.
        '''

        return CommandResponseType.OK, 'show start'

    def stop(self):
        '''
        Método principal para parar compartilhamento de pacotes e limpar
        regras executadas no iptables.
        '''

        return CommandResponseType.OK, 'show stop'

    def run(self):
        code = CommandResponseType.ERROR

        args = self.get_args()
        if not (args and len(args) >= 1):
            message = "Não há argumentos suficientes!"
            return (code, message)

        available_actions = {
            'start': self.start,
            'stop': self.stop
        }

        action = args.pop(0)
        if action not in available_actions or args:
            message = "Ação inválida!"
            return (code, message)

        return available_actions[action]()


def get_client_commands():
    return [
        ClearCommand(),
        HelpCommand(),
        ExitCommand()
    ]


def get_server_commands():
    return [
        UserCommand(),
        RuleCommand(),
        FirewallCommand()
    ]
