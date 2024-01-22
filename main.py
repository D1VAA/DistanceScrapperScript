from src.modules.sheet_handler import SheetHandler
from src.modules.scrapper import ScrapFromFile

scrap = ScrapFromFile('./cotacao.xlsx',option=2)
scrap.run()