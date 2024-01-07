from api.api import run_api
from menu.menu_builder import MenuBuilder
from src.modules.scrapper import ScrapFromFile

menu = MenuBuilder('main')
menu.add_opts('api', run_api, 'Api')
menu.add_opts('setup', ScrapFromFile, '.')
menu.add_opts('scrapfile', ScrapFromFile.run, 'Executa o ScrapFromFile')
menu.add_cmds('use', menu.use, 'Configura as funções.')
menu.add_cmds('show menu', menu.printer, 'Mostra o menu')
menu.run()
