from typing import Callable, Tuple
from menu.src.utils.bcolors import Colors
from menu.src.manage_panels import ManagePanels 
import inspect

class ConfigPanel(ManagePanels):
    """
    This class uses some resources from the ManagePanels, to build a Panel that allow the user to configurate parameters and execute functions that were added as an [opt].
    """
    _data = {}
    @property
    def data(self):
        return self._data
    
    def use(self, obj: Callable, mock_input=None):
        self.func_name: str = obj.__name__
        self.func = obj 

        self.use_instance = ManagePanels('use')
        input_format = f'{self.use_instance.panel} ({Colors.RED}{self.func_name}{Colors.RESET})>'

        if self.func_name in self.data: 
            self._params = self.data[self.func_name]
        else:
            self.data[self.func_name] = self.obj_params(obj)
            self._params = self.data[self.func_name]
        [self.use_instance.add_opts(param, desc=value) for param, value in self._params.items()]
        self.use_instance.add_cmds('show options', self.use_instance.printer, 'Mostra esse menu')
        self.use_instance.add_cmds('set', self._update_parameters, 'Configura os valores dos parâmetros.')
        self.use_instance.add_cmds('run', self._execute, 'Roda a função')
        if mock_input is not None:
            self.use_instance.opt = mock_input  # type: ignore
        else:
            self.use_instance.run(input_format=input_format)
        
        return self
    
    @staticmethod
    def obj_params(obj: Callable | Tuple) -> dict[str, str]:
        """
        Method that receives an object and extracts all its parameters.
        """
        params = {}
        def extract_params(sig):
            for param_name, param in sig.parameters.items():
                if param_name not in ['self', 'cls'] and param.default != inspect.Parameter.empty:
                    params[param_name] = param.default
        if isinstance(obj, tuple):
            for item in obj:
                if inspect.isclass(item):
                    extract_params(inspect.signature(item.__init__))
                else:
                    extract_params(inspect.signature(item))
        else:
            if inspect.isclass(obj):
                extract_params(inspect.signature(obj.__init__))
            else:
                extract_params(inspect.signature(obj))
        return params

    def _update_parameters(self, parameter: str, new_value: str):
        if parameter not in self.use_instance.opts_keys:
            print(f"{Colors.RED}[!]{Colors.RESET} Parâmetro: {parameter} não encontrado...")
        elif ':' in new_value:
            self._handle_relative_reference(parameter, new_value)
        else:
            self._update_single_parameter(parameter, new_value)
    
    def _handle_relative_reference(self, parameter, new_value):
        ref, opt = new_value.split(':')
        if ref in self.instances and opt in self.instances[ref].opts_keys:
            print(f"\n{Colors.BLUE}[+]{Colors.RESET} Relative reference found...", end= '\t')
            print(f"{Colors.BLUE}PANEL:{Colors.RESET} [{ref}] {Colors.BLUE}OPT:{Colors.RESET} [{opt}]n\n")
            instance = self.instances[ref]
            ref_opt = instance.opts[opt]['func']
            if ref_opt.__name__ == self.func.__name__:
                print(f"\n{Colors.RED}[!]{Colors.RESET} Invalid operation...\n")
                return
            else:
                self._params[parameter] = ref_opt
                self.data[self.func_name][parameter] = ref_opt
        else:
            print(f'{Colors.RED}[!]{Colors.RESET} Invalid relative reference...\n')
        self._update_printer_method(parameter, new_value)
    
    def _update_single_parameter(self, parameter, new_value):
        self._params[parameter] = new_value
        self.data[self.func_name][parameter] = new_value
        self._update_printer_method(parameter, new_value)
    
    def _update_printer_method(self, parameter, new_value):
        self.use_instance.opts[parameter]['desc'] = new_value
        self.use_instance.printer(opt='opts')

    def _execute(self):
        print(f'{Colors.BLUE}[-]{Colors.RESET} Running...')
        print(f"{'-'*60}\n\n")
        if inspect.isclass(self.func):
            msg = f"|{'-'*3}> Instance Created"
            print(msg, end='\n\n')
            result = self.func(**self._params)
            self.data[self.func_name]['instance'] = result
        else:
            if inspect.ismethod(self.func):
                print(f"|{'-'*3}> Loading Instance", end='\n\n')
                class_name = self.func.__qualname__.split('.')[0]
                instance = self.data[class_name]['instance']
                method = self.func
                method(instance, **self._params)
            else:
                self.func(**self._params)
