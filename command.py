from types import FunctionType
from typing import Dict, List
from json import dumps, loads
from os import system

from command_response_type import CommandResponseType, DatabaseTableType
from models import User, Rule

IFACE_LAN = 'enp0s8'
IFACE_WAN = 'enp0s3'
USER_LOGGED_IN = None


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
            "- Entrar em um usuário cadastrado no servidor:",
            "$ user login <email> <senha>\n",
            "- Sair de conta cadastrada em servidor:",
            "$ user logout\n",
            "- Listar todos usuários:",
            "$ user list all\n",
            "- Remover usuário:",
            "$ user remove <email ou ID>\n",
            "- Criar nova regra de firewall:",
            "$ rule add <ip address> <action>, action deve ser ACCEPT ou DENY\n",
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

    def get_table_from_database(self, table: DatabaseTableType):
        '''
        Retorna uma tabela do banco de dados.
        '''

        content = self.get_database_content()
        available_tables = {
            DatabaseTableType.USER: "users",
            DatabaseTableType.RULE: "rules"
        }

        selected_table = available_tables.get(table)
        if not selected_table:
            return None

        return loads(content).get(selected_table)

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
            'login': self.login_user,
            'logout': self.logout_user
        }

    def check_if_unique_user_in_database(self, user: User):
        '''
        Verifica se um usuário já foi cadastrado com o e-mail passado.
        '''

        users = self.get_table_from_database(DatabaseTableType.USER)

        for id in users:
            usr = users[id]
            email = usr['email']

            if email == user.email:
                return False

        return True

    def add_user_to_database(self, user: User):
        '''
        Abre o arquivo .json de banco de dados e atualiza a seção de 'users'
        com o novo usuário.
        '''

        code = CommandResponseType.ERROR

        db = {}

        content = self.get_database_content()
        db.update(loads(content))

        if not self.check_if_unique_user_in_database(user):
            message = 'Usuário já cadastrado com este e-mail!'
            return (code, message)

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

        users = self.get_table_from_database(DatabaseTableType.USER)

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

    def check_if_user_exists(self, email: str, password: str):
        '''
        Verifica se um usuário existe no banco de dados.
        '''

        users = self.get_table_from_database(DatabaseTableType.USER)

        for id in users:
            usr = users[id]

            same_email = email == usr['email']
            same_password = User.check_password(password, usr['password'])

            validation = same_email and same_password

            if validation:
                result = User.new_from_dict(id, usr)
                return result

        return False

    def remove_user(self, args: List[str]):
        '''
        Método principal chamado para remover um usuário do banco de dados.
        '''

        global USER_LOGGED_IN
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

                if USER_LOGGED_IN:
                    logged_user_id = USER_LOGGED_IN.id
                    if user_id == logged_user_id:
                        message = 'Não é possível remover um usuário logado!'
                        return (code, message)

                user_list.pop(user_id)

                database['users'] = user_list

                self.save_dict_to_database(database)

                code = CommandResponseType.OK
                message = "Usuário removido com sucesso!"
                return (code, message)

        message = "Usuário não encontrado!"
        return (code, message)

    def login_user(self, args: List[str]):
        '''
        Realiza o login de usuário após esse fornecer o email e senha corretos.
        '''

        global USER_LOGGED_IN
        code = CommandResponseType.ERROR

        if len(args) != 2:
            message = "Número de argumentos inválido!"
            return (code, message)

        if USER_LOGGED_IN:
            message = 'Usuário já logado!'
            return (code, message)

        email, password = args
        result = self.check_if_user_exists(email, password)

        if not result:
            message = 'E-mail ou senha inválidos!'
            return (code, message)

        USER_LOGGED_IN = result

        code = CommandResponseType.OK
        message = 'Login realizado com sucesso!'

        return (code, message)

    def logout_user(self, args: List[str]):
        '''
        Desloga um usuário de sua conta.
        '''

        code = CommandResponseType.ERROR
        global USER_LOGGED_IN

        if args:
            message = 'Quantia de argumentos inválidos!'
            return (code, message)

        if not USER_LOGGED_IN:
            message = 'Usuário não está logado!'
            return (code, message)

        USER_LOGGED_IN = None

        code = CommandResponseType.OK
        message = 'Logout realizado com sucesso!'

        return (code, message)


class RuleCommand(DatabaseCommand):
    name = "rule"

    def __init__(self):
        self.available_actions = {
            'add': self.add_rule,
            'list': self.list_rules,
            'remove': self.remove_rule,
        }

    def check_if_unique_rule_in_database(self, rule: Rule):
        rules = self.get_table_from_database(DatabaseTableType.RULE)

        for id in rules:
            r = rules[id]
            address = r['ip']

            if address == rule.ip:
                return False

        return True

    def add_rule_to_database(self, rule: Rule):
        '''
        Abre o arquivo .json de banco de dados e atualiza a seção de 'rules'
        com a nova regra.
        '''

        code = CommandResponseType.ERROR

        content = self.get_database_content()
        db = loads(content)

        if not self.check_if_unique_rule_in_database(rule):
            message = 'Já existe uma regra para este endereço!'
            return (code, message)

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
                f'ID: {x[0]}\n' +
                f'Endereço IP: {x[1]["ip"]}\n' +
                f'Ação: {x[1]["action"]}\n',
                rules
            ))

    def get_rules_by_user_id(self, user_id):
        rules = self.get_table_from_database(DatabaseTableType.RULE)

        if not rules:
            rules = {}

        available_rule_ids = list(
            filter(
                lambda x: rules[x]['user_id'] == user_id,
                rules
            )
        )

        result = [[i, rules[i]] for i in available_rule_ids]

        return self.parse_rule_list_as_string(result)

    def get_rules_from_database(self):
        '''
        Retorna as regras do banco de dados na seção 'rules'.
        '''

        global USER_LOGGED_IN
        user_id = USER_LOGGED_IN.id

        rules = self.get_rules_by_user_id(user_id)

        return rules

    def add_rule(self, args: List[str]):
        '''
        Método principal chamado para adicionar uma regra no banco de dados.
        '''

        global USER_LOGGED_IN
        code = CommandResponseType.ERROR

        if len(args) != 2:
            message = "Número de argumentos inválido!"
            return (code, message)

        ip, action = args
        available_actions = ["ACCEPT", "DENY"]

        if action not in available_actions:
            message = "Ação inválida!"
            return (code, message)

        if not USER_LOGGED_IN:
            message = "É preciso estar logado para definir regras no iptables!"
            return (code, message)

        id = USER_LOGGED_IN.id
        rule = Rule(id, ip, action)

        return self.add_rule_to_database(rule)

    def list_rules(self, args: List[str]):
        '''
        Método principal chamado para listar regras no banco de dados.
        '''

        global USER_LOGGED_IN
        code = CommandResponseType.ERROR

        if len(args) != 1:
            message = "Número de argumentos inválido!"
            return (code, message)

        flag = args.pop()
        if flag != 'all':
            message = "Sinalizador inválido!"
            return (code, message)

        if not USER_LOGGED_IN:
            message = 'É necessário estar logado para ver regras do iptables!'
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

        global USER_LOGGED_IN
        code = CommandResponseType.ERROR

        if len(args) != 1:
            message = "Número de argumentos inválido!"
            return (code, message)

        if not USER_LOGGED_IN:
            message = 'É necessário estar logado para remover regras do iptables!'
            return (code, message)

        address_or_id = args.pop()

        content = self.get_database_content()
        database = loads(content)
        rule_list = database.get("rules")

        user_id = USER_LOGGED_IN.id

        for rule_id in rule_list:
            rule = rule_list[rule_id]
            if rule['user_id'] != user_id:
                continue

            if address_or_id in [rule_id, rule.get("ip")]:
                rule_list.pop(rule_id)

                database['rules'] = rule_list

                self.save_dict_to_database(database)

                code = CommandResponseType.OK
                message = "Regra removida com sucesso!"
                return (code, message)

        message = "Regra não encontrada!"
        return (code, message)


class FirewallCommand(DatabaseCommand):
    name = "firewall"

    def run_script_file(self, file: str, args=[]):
        '''
        Abre um arquivo na pasta "./scripts" e executa de acordo com os
        argumentos passados.
        '''

        with open(file, mode='r') as file:
            commands = file.readlines()

            for line in commands:
                if not line.strip():
                    continue

                command = line.format(*args)
                print(f"$ {command}")
                error = system(command)

                if error:
                    return False

        return True

    def clear_iptables_rules(self):
        '''
        Limpa as regras definidas no iptables.
        '''

        # clear_iptables_file = "../scripts/clear_iptables_rules.script"

        # with open(clear_iptables_file, mode="r") as file:
        #     commands = file.readlines()
        #     for iptables_command in commands:
        #         system(iptables_command)
        file = '../scripts/clear_iptables_rules.script'
        result = self.run_script_file(file)

        return result

    def enable_internet_via_nat(self):
        '''
        Permite a conversão de ip privado para público através do masquerade.
        '''

        file = "../scripts/enable_internet_via_nat.script"
        result = self.run_script_file(file)
        return result

        # with open(file, mode="r") as file:
        #     command = file.readlines()[0]
        #     system(command)

    def enable_ip_forwarding(self, enable: bool):
        '''
        Permite o encaminhamento de pacotes.
        '''

        file = "../scripts/change_ip_forwarding.script"
        args = [int(enable)]
        result = self.run_script_file(file, args)

        return result

        # with open(file, mode="r") as file:
        #     command = file.readlines()[0].format(int(enable))
        #     system(command)

    def set_address_permission_in_iptables(self, address: str, action: str):
        '''
        Aplica uma regra individual a um endereço, permitindo ou não seu acesso 
        à internet.        
        '''

        file = "../scripts/address_action_to_server.script"
        args = [IFACE_LAN, IFACE_WAN, address, action]
        result = self.run_script_file(file, args)

        return result

        # with open(address_action_to_server_file, mode="r") as file:
        #     commands = file.readlines()
        #     for address_action in commands:
        #         system(
        #             address_action.format(
        #                 IFACE_LAN,
        #                 IFACE_WAN,
        #                 address,
        #                 action
        #             )
        #         )

    def apply_rules_to_iptables(self, rule_list):
        '''
        Aplica as regras definidas no banco de dados para cada endereço, 
        permitindo ou restringindo o acesso à internet.
        '''

        global USER_LOGGED_IN
        user_id = USER_LOGGED_IN.id

        for rule_id in rule_list:
            rule = rule_list[rule_id]
            if rule['user_id'] != user_id:
                continue

            ip, action = rule.get("ip"), rule.get("action")

            if action == "DENY":
                action = "DROP"

            result = self.set_address_permission_in_iptables(ip, action)
            if not result:
                return False

        return True

    def start(self):
        '''
        Método principal para permitir compartilhamento de pacotes e
        executar regras salvas no banco de dados no iptables.
        '''

        code = CommandResponseType.ERROR

        self.enable_internet_via_nat()
        self.enable_ip_forwarding(True)

        rule_list = self.get_table_from_database(DatabaseTableType.RULE)

        if rule_list is None:
            message = "Não foi possível obter regras cadastradas no banco de dados!"
            return (code, message)

        result = self.apply_rules_to_iptables(rule_list)

        if not result:
            message = "Houve algum erro durante a execução dos scripts!"
            return (code, message)

        code = CommandResponseType.OK
        message = 'Regras de firewall aplicadas com sucesso!'

        return (code, message)

    def stop(self):
        '''
        Método principal para parar compartilhamento de pacotes e limpar
        regras executadas no iptables.
        '''

        code = CommandResponseType.ERROR

        results = [
            self.enable_ip_forwarding(False),
            self.clear_iptables_rules()
        ]

        if not all(results):
            message = "Houve algum erro durante a execução dos scripts!"
            return (code, message)

        code = CommandResponseType.OK
        message = 'Regras de firewall redefinidas com sucesso!'

        return (code, message)

    def run(self):
        global USER_LOGGED_IN
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

        if not USER_LOGGED_IN:
            message = 'É preciso estar logado para executar regras do iptables!'
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
