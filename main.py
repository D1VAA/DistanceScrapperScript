from src.modules.sheet_handler import SheetHandler
from src.modules.scrapper import ScrapFromFile
import asyncio


scrap = ScrapFromFile('./cotacao.xlsx',option=2)
scrap.run()