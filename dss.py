from api.api import run_server
from menu.menu_builder import MenuBuilder
from src.modules.sheet_handler import SheetHandler

menu = MenuBuilder('main')
menu.add_opts('api', run_server, 'Api')
menu.add_opts('SheetHandler', SheetHandler, 'Manipulador de planilha (xlsx).')
menu.add_cmds('use', menu.use, 'Configura as funções.')
menu.run()
