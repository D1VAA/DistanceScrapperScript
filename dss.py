from src.api.api import run_api
from menu.menu_builder import MenuBuilder
from src.modules.scrapper import ScrapFromFile

menu = MenuBuilder('main')
menu.add_opts('api', run_api, 'Api')
menu.add_opts('scrap', ScrapFromFile, 'Scrap from file')
menu.add_cmds('show options', menu.printer, 'Mostra o menu')
menu.add_cmds('use', menu.use, 'Configura os modulos.')
menu.run()
