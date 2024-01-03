from menu.src.utils.bcolors import Colors
from typing import Literal, Optional, Callable

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
        self.panel_data = {'opts': {}, 'cmds': {}}
        self.opts = self.panel_data['opts']
        self.cmds = self.panel_data['cmds']
        self.cmds_keys = self.cmds.keys()
        self.opts_keys = self.opts.keys()
    
    @property
    def instances(self) -> dict:
        return self._instances

    def add_opts(self, nick: str, func: Optional[Callable] = None, desc: Optional[str] = None):
        self.opts[nick] = {'func': func, 'desc': str(desc)}

    def add_cmds(self, nick: str, func: Optional[Callable], desc: Optional[str] = None):
        self.cmds[nick] = {'func': func, 'desc': str(desc)}
    
    def printer(self, opt: Optional[Literal['opts' , 'cmds']]=None):
        print('\n\n')
        cmd_format = f'{"=" * 25} COMANDOS {"=" * 25}'
        opt_format = f'\n{"=" * 26} OPÇÕES {"=" * 26}'
        if opt == 'cmds':
            print(cmd_format, end='\n\n')
            for nick, infos in self.cmds.items():
                description = infos['desc']
                print(f'{Colors.RED}[-] {nick} {Colors.RESET}> {description}', end='\n')
        elif opt == 'opts': 
            print(opt_format, end='\n\n')
            for nick, infos in self.opts.items():
                description = infos['desc']
                print(f'{Colors.BLUE}[+] {nick} {Colors.RESET}> {description}', end='\n')
        else:
            print(cmd_format, end='\n\n')
            for nick, infos in self.cmds.items():
                description = infos['desc']
                print(f'{Colors.RED}[-] {nick} {Colors.RESET}> {description}', end='\n')
            print(opt_format, end='\n\n')
            for nick, infos in self.opts.items():
                description = infos['desc']
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
                        args = [self.opts[x]['func'] if (x in self.opts_keys and self.opts[x]['func'] is not None) else x for x in args]
                        self.cmds[cmd]['func'](*args)
                else:
                    self.cmds[opt]['func']()

            except Exception as e:
                print(f'{Colors.RED}[!] ERROR >>> {Colors.RESET}', str(e))
