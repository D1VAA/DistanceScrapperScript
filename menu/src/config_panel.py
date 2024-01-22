from typing import Callable, Dict
from menu.src.utils.bcolors import Colors
from menu.src.manage_panels import ManagePanels 
import inspect
import ast

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
    def obj_params(obj: Callable) -> Dict:
        """
        Method that receives an object and extracts all its parameters.
        """
        params = {}
        def extract_params(sig):
            for param_name, param in sig.parameters.items():
                if param_name not in ['self', 'cls'] and param.default != inspect.Parameter.empty:
                    params[param_name] = param.default
                elif param_name not in ['self', 'cls']:
                    params[param_name] = 'No default value'
        if inspect.isclass(obj):
            extract_params(inspect.signature(obj.__init__))
        else:
            extract_params(inspect.signature(obj))
        return params

    def _update_parameters(self, parameter: str, new_value: str) -> None:
        """Method called when the set command is called."""
        if parameter not in self.use_instance.opt_keys:
            print(f"{Colors.RED}[!]{Colors.RESET} Parâmetro: {parameter} não encontrado...")

        elif ':' in new_value:
            ref, opt = new_value.split(':')
            # Verify if the 'ref' is a panel name and the 'opt' is present in that panel
            if ref in self.instances and opt in self.instances[ref].opts_keys:
                self._handle_relative_reference(parameter, new_value)

            elif ref in ['bool', 'int', 'float']:
                self._force_type(parameter, ref, opt)

            else:
                print(f'{Colors.RED}[!]{Colors.RESET} Invalid operation...\n')

        else:
            self._update_single_parameter(parameter, new_value)
    
    def _handle_relative_reference(self, parameter: str, new_value: str) -> None:
        """
        Method to handle relative references.
        Relative reference occurr when the new value of a parameter is another function.

        Syntax : 'panel_name:function_nickname'
        """
        ref, opt = new_value.split(':')
        print(f"\n+ Relative reference found...", end= '\t')
        print(f"{Colors.BLUE}PANEL:{Colors.RESET} [{ref}] {Colors.BLUE}OPT:{Colors.RESET} [{opt}]n\n")
        instance = self.instances[ref]
        ref_opt = instance.opts[opt]['func']
        if ref_opt.__name__ == self.func.__name__:
            print(f"\n{Colors.RED}[!]{Colors.RESET} Invalid operation...\n")
            return
        else:
            self._params[parameter] = ref_opt
            self.data[self.func_name][parameter] = ref_opt
        self._update_printer_method(parameter, new_value)
    
    def _update_single_parameter(self, parameter: str, new_value:str) -> None:
        """Method to update a single parameter without any verification."""
        self._params[parameter] = new_value
        self.data[self.func_name][parameter] = new_value
        self._update_printer_method(parameter, new_value)

    def _force_type(self, parameter: str, ref: str, opt: str) -> None:
        """
        Method to force a type for the value of the parameter.
        Syntax: 'type:value'
        """
        allowed_types = {'bool': ast.literal_eval, 'float': float, 'int': int}
        new_value = allowed_types[ref](str(opt))
        self._update_single_parameter(parameter, new_value)

    def _update_printer_method(self, parameter: str, new_value: str) -> None:
        """
        Method that will update the printer method of Manage Panels after change a parameter value.
        """
        self.use_instance.panel_opts[parameter].description = new_value
        self.use_instance.printer()

    def _execute(self) -> None:
        """Method to execute a function, create a instance or call a method.
        For classes, the method create a instance and save in the data dictionary with the function name and the key word 'instance', to make easier to call methods using a respective instance."""
        print(f'{Colors.BLUE}[-]{Colors.RESET} Running...')
        print(f"+{'-'*28}+\n")
        try:
            if inspect.isclass(self.func):
                result = self.func(**self._params)
                # Verifiy if it's a method.
                methods = inspect.getmembers(self.func, predicate=inspect.isfunction)
                self.data[self.func_name]['instance'] = result
                print('+ Instance created!', end='\n\n')
                self.data[self.func_name]['methods'] = methods
            elif self.func.__qualname__.split('.')[1] in self.data[self.func.__qualname__.split('.')[0]]['methods']:
                class_name = self.func.__qualname__.split('.')[0]
                instance = self.data[class_name]['instance']
                method = self.func
                print(f"+ Loading Instance", end='\n\n')
                method(instance, **self._params)

        # If the callable is not a method or a class, must be a function.
        except:
            self.func(**self._params)
