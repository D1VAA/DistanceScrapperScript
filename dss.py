from api.api import run_api
from menu.menu_builder import MenuBuilder
from src.modules.sheet_handler import SheetHandler

menu = MenuBuilder('main')
menu.add_opts('api', run_api, 'Api')
menu.add_opts('SheetHandler', SheetHandler, 'Manipulador de planilha (xlsx).')
menu.add_cmds('use', menu.use, 'Configura as funções.')
menu.run()
