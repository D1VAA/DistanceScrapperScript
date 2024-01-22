import aiohttp
import asyncio
import pandas as pd
from dataclasses import dataclass
from src.modules.sheet_handler import SheetHandler
from typing import Union, List, Dict, Tuple, Literal
from bs4 import BeautifulSoup
headers = {
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0'
}
google_url = f'https://www.google.com/search?q=distância entre '

async def simple_distance_scrapper(session, origin: str, destination: str) -> Union[float, str, None]:
    """Function that scrap the distance of two cities from google using requests lib."""
    # ------------------------
    string = f'{origin} e {destination}'
    url = f'{google_url}{string}'
    # ------------------------

    async with session.get(url, headers=headers) as response:
        html = await response.text() 
        soup = BeautifulSoup(html, 'html.parser')
        span = soup.find('span', class_='UdvAnf')
        if span is not None:
            for item in span:
                span_text = item.text  #type: ignore
                if 'km' in span_text:
                    km_str = span_text[:-3].replace(".", "").replace(",", ".")
                    distance = float(km_str)
                    return distance
        else:
            return 'Distance not found.'

@dataclass
class Route:
    origin: str
    dest: str
    url: str
    key: str = None  # type: ignore
    distance: Union[float, str, None] = None
    def __post_init__(self):
        if self.key is None:
            self.key = f'{self.origin} x {self.dest}'

class ScrapFromFile(SheetHandler):
    def __init__(self, path: str, option: Literal[1,2]):
        super().__init__(path, option)
        # O dicionário query_dict salva as instâncias de Route, por uma key que é simplesmente uma string com a origem e o destino separados por um 'x'
        self._query_dict: Dict[str, Route] = dict()
        self._create_querys()
        self.run()
    
    def _create_querys(self) -> None:
        """Method to create a list with all Route instances and their corresponding urls.
        The method proceeds to save all the instances in self._query_dict using the instance key, that is automatically generated.
        """
        for origin, dest in self.cities_combination.items():
            for destination in dest:
                string = f'{origin} e {destination}'
                url = f'{google_url}{string}'
                instance = Route(origin, destination, url=url)
                self._query_dict[instance.key] = instance
                
    async def _create_session(self) -> None:
        self.session = aiohttp.ClientSession()
    
    async def _close_session(self) -> None:
        await self.session.close()
    
    async def _core(self) -> None:
        await self._create_session()
        tasks: List[asyncio.Task] = list()
        try:
            for key, route in self._query_dict.items():
                tasks.append(asyncio.create_task(self._requester(route.url, key)))

            results = await asyncio.gather(*tasks)
            for key, distance in results:
                self._query_dict[key].distance = distance
        except Exception as e:
            print("Exception: ",e)
        finally:
            await self._close_session()

    async def _requester(self, url: str, route_key: str) -> Tuple[str, str|float]:
        """This method does the request and returns the html."""
        try:
            async with self.session.get(url, headers=headers) as response:
                # If the program receive 429 HTTP Code (Too Many Requests), it proceeds closing the actual session and open a new session.
                if response.status == 429:
                    print(f'Received 429 status code. Creating a new session.')
                    await self._close_session()
                    await self._create_session()
                    await asyncio.sleep(3)
                    return await self._requester(url, route_key)

                else:
                    html = await response.text()
                    distance = await self._parser(html)
                    return (route_key, distance)

        except aiohttp.ClientError as e:
            print(f'Error fecthing data for {route_key}: {e}')
            return route_key, ''

    async def _parser(self, html) -> Union[float, str]:
        """Function that tries to extract the distance from the html and then converts to float and return it. If the distance is not found, the method return 'Distância não encontrada.'. """
        soup = BeautifulSoup(html, 'html.parser')
        try:
            span = soup.find('span', class_='UdvAnf')
            for item in span:  # type: ignore
                span_text = item.text  # type: ignore
                if 'km' in span_text:
                    km_str = span_text[:-3].replace(".", "").replace(",", ".")
                    km = float(km_str)
                    return km
            return 'Não enontrado.'

        except Exception:
            return 'Não encontrado.'
    
    def run(self):
        asyncio.run(self._core())
        self._export()
    
    def _export(self):
        """Method to export the data extracted to Excel file."""
        distance_col: List[float|str|None] = []  # Lista que será utilizada para criar a coluna de distâncias no dataframe.
        for origin, dest in zip(self.origin, self.destination):
            string = f'{origin} x {dest}' 
            distance_col.append(self._query_dict[string].distance)

        df = pd.DataFrame({'Origem': self.origin,
                           'Destino': self.destination,
                           'Distância': distance_col})
        df.to_excel('./Result.xlsx')
