from menu.src.utils.bcolors import Colors
from typing import Literal, Optional, Callable, Dict
from dataclasses import dataclass

@dataclass
class PanelObject:
    nick: str
    func: Optional[Callable] = None
    description: Optional[str] = None

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
        self.panel_opts: Dict[str, PanelObject] = {}
        self.panel_cmds: Dict[str, PanelObject] = {}
    
    @property
    def cmd_keys(self):
        return [nick for nick in self.panel_cmds.keys()]
    
    @property
    def opt_keys(self):
        return [nick for nick in self.panel_opts.keys()]
    
    @property
    def instances(self) -> dict:
        return self._instances

    def add_opts(self, nick: str, func: Optional[Callable] = None, desc: Optional[str] = None):
        self.panel_opts[nick] = PanelObject(nick, func, desc)

    def add_cmds(self, nick: str, func: Optional[Callable], desc: Optional[str] = None):
        self.panel_cmds[nick] = PanelObject(nick, func, desc)
    
    def printer(self, opt: Optional[Literal['opts' , 'cmds']]=None):
        """Método para printar todos os comandos e opções que foram adicionados ao menu."""
        print('\n')
        cmd_format = f'{"=" * 25} COMANDOS {"=" * 25}'
        opt_format = f'\n{"=" * 26} OPÇÕES {"=" * 26}'
        # Se o parâmetro opt for 'cmds' o comando ao ser chamado irá mostrar somente a seção de comandos
        if opt == 'cmds':
            print(cmd_format, end='\n\n')
            for nick, cmd in self.panel_cmds.items():
                description = cmd.description
                print(f'{Colors.RED}[-] {nick} {Colors.RESET}> {description}', end='\n')
        # Se o parâmetro opt for 'opts' o comando ao ser chamado irá mostrar somente a seção de opções.
        elif opt == 'opts': 
            print(opt_format, end='\n\n')
            for nick, option in self.panel_opts.items():
                description = option.description
                print(f'{Colors.BLUE}[+] {nick} {Colors.RESET}> {description}', end='\n')
        # Mostra as duas seções.
        else:
            print(cmd_format, end='\n\n')
            for nick ,cmd in self.panel_cmds.items():
                description = cmd.description
                print(f'{Colors.RED}[-] {nick} {Colors.RESET}> {description}', end='\n')
            print(opt_format, end='\n\n')
            for nick, option in self.panel_opts.items():
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
                if opt not in self.cmd_keys:
                    cmd, *args = opt.split()
                    # Replace the nick with the function obj
                    cmd_obj = self.panel_cmds[cmd]
                    # Crie uma lista de argumentos substituindo os nicks pelos objetos de função correspondentes
                    args = [self.panel_opts[arg].func 
                            if (arg in self.opt_keys and self.panel_opts[arg].func is not None) 
                            else arg 
                            for arg in args]
                    cmd_obj.func(*args)  # type: ignore
                else:
                    self.panel_cmds[opt].func()  # type:ignore

            except AttributeError:
                print(f'{Colors.RED}[!]{Colors.RESET} Função não encontrada.')
            except TypeError:
                print(f'{Colors.RED}[!]{Colors.RESET} Faltando um ou mais parâmetros obrigatórios.')
            except KeyError:
                print(f'{Colors.RED}[!]{Colors.RESET} Comando Inválido!')
            except ValueError as e:
                print(f"Value Error:", e)
            except Exception as e:
                print(e)
    