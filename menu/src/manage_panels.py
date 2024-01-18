from menu.src.utils.bcolors import Colors
from typing import Literal, Optional, Callable, List
from dataclasses import dataclass

@dataclass
class PanelObject:
    nick: str
    function: Optional[Callable] = None
    description: Optional[str] = None

    def __iter__(self):
        yield self.nick
        yield self.function
        yield self.description

class ManagePanels:
    _instances = {}
    def __new__(cls, *args, **kwargs):
        panel = args[0] if args else kwargs.get('panel')
        if panel not in cls._instances.keys(): 
            new_instance = super().__new__(cls)
            cls._instances[panel] = new_instance
            return new_instance
        return cls._instances[panel]

    def __init__(self, panel:str):
        self.panel = str(panel)
        self.panel_opts: List[PanelObject] = []
        self.panel_cmds: List[PanelObject] = []
        self.opts = [item for item in self.panel_opts]
        self.cmds = [item for item in self.panel_cmds]
        self.cmds_keys = [item.nick for item in self.panel_cmds]
        self.cmds_keys = [item.nick for item in self.panel_opts]
    
    @property
    def instances(self) -> dict:
        return self._instances

    def add_opts(self, nick: str, func: Optional[Callable] = None, desc: Optional[str] = None):
        self.panel_opts.append(PanelObject(nick, func, desc))

    def add_cmds(self, nick: str, func: Optional[Callable], desc: Optional[str] = None):
        self.panel_cmds.append(PanelObject(nick, func, desc))
    
    def printer(self, opt: Optional[Literal['opts' , 'cmds']]=None):
        """Método para printar todos os comandos e opções que foram adicionados ao menu."""
        print('\n')
        cmd_format = f'{"=" * 25} COMANDOS {"=" * 25}'
        opt_format = f'\n{"=" * 26} OPÇÕES {"=" * 26}'
        # Se o parâmetro opt for 'cmds' o comando ao ser chamado irá mostrar somente a seção de comandos
        if opt == 'cmds':
            print(cmd_format, end='\n\n')
            for cmd in self.panel_cmds:
                nick = cmd.nick
                description = cmd.description
                print(f'{Colors.RED}[-] {nick} {Colors.RESET}> {description}', end='\n')
        # Se o parâmetro opt for 'opts' o comando ao ser chamado irá mostrar somente a seção de opções.
        elif opt == 'opts': 
            print(opt_format, end='\n\n')
            for option in self.panel_opts:
                nick = option.nick
                description = option.description
                print(f'{Colors.BLUE}[+] {nick} {Colors.RESET}> {description}', end='\n')
        # Mostra as duas seções.
        else:
            print(cmd_format, end='\n\n')
            for cmd in self.panel_cmds:
                nick = cmd.nick
                description = cmd.description
                print(f'{Colors.RED}[-] {nick} {Colors.RESET}> {description}', end='\n')
            print(opt_format, end='\n\n')
            for option in self.panel_opts:
                nick = option.nick
                description = option.description

                print(f'{Colors.BLUE}[+] {nick} {Colors.RESET}> {description}', end='\n')
        print('\n\n')

    def run(self, input_format: Optional[str]=None):
        self.printer()
        df_format = f'({Colors.RED}{self.panel}{Colors.RESET})>' if input_format is None else input_format
        while True:
            opt = input(f'{df_format} ')
            try:
                if opt in ['exit', 'quit']:
                    break
                # If the input isn't a cmd (like "show options"), must be a cmd and an opt (cmd + opt)
                if opt not in self.cmds_keys:
                        cmd, *args = opt.split()

                        # Replace the nick with the function obj
                        functions_list = {opt.nick:opt.function for opt in self.panel_opts}
                        args = [self.opts[x]['func'] if (x in self.opts_keys and self.opts[x]['func'] is not None) else x for x in args]
                        self.cmds[cmd]['func'](*args)
                else:
                    self.cmds[opt]['func']()

            except AttributeError:
                print(f'{Colors.RED}[!]{Colors.RESET} Função não encontrada.')
            except TypeError:
                print(f'{Colors.RED}[!]{Colors.RESET} Faltando um ou mais parâmetros obrigatórios.')
            except KeyError:
                print(f'{Colors.RED}[!]{Colors.RESET} Comando Inválido!')
            except ValueError:
                print()
            except Exception as e:
                print(e)
    