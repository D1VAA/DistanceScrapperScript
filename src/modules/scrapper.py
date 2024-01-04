import requests
import asyncio
from dataclasses import dataclass
from pandas import Series
from typing import Union, List, Dict, Tuple
from bs4 import BeautifulSoup

headers = {
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0'
}
google_url = f'https://www.google.com/search?q=distância entre '

async def simple_distance_scrapper(origin: str, destination: str) -> Union[float, str, None]:
    """Function that scrap the distance of two cities from google using requests lib."""
    # ------------------------
    string = f'{origin} e {destination}'
    url = f'{google_url}{string}'
    # ------------------------

    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, 'html.parser')
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
            self.key = f'{self.origin}x{self.dest}'

class Scrapper:
    def __init__(self, origin: Series, destination: Series):
        self._origin = origin
        self._destination = destination
        self._query_dict: Dict[str, Route] = dict()
        self._create_querys()
    
    def _create_querys(self) -> None: 
        """Method to create a list with all Route instances and their corresponding urls.
        The method proceeds to save all the instances in self._query_dict using the instance key, that is automatically generated.
        """
        for origin, dest in zip(self._origin, self._destination):
            string = f'{origin} e {dest}'
            url = f'{google_url}{string}'
            instance = Route(origin, dest, url=url)
            self._query_dict[instance.key] = instance
    
    async def run(self) -> None:
        s = requests.Session()
        tasks: List[asyncio.Task] = list()
        try:
            for key, route in self._query_dict.items():
                task = asyncio.create_task(self._requester(s, route.url, key))
                tasks.append(task)

            for coro in asyncio.as_completed(tasks):
                key, html = await coro
                if html != '':
                    km = await self._parser(html)
                    self._query_dict[key].distance = km
        finally:
            s.close()

    @staticmethod
    async def _requester(session: requests.Session, url: str, route_key: str) -> Tuple[str, str]:
        """This method does the request and returns the html."""
        try:
            response = await asyncio.to_thread(session.get, url)
            response.raise_for_status()
            return (route_key, response.text)
        except Exception as e:
            print(f'Error fecthing data for {route_key}: {e}')
            return route_key, ''

    @staticmethod
    async def _parser(html) -> Union[float, str]:
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
            return 'Not found.'

        except AttributeError:
            print('Error occurred while searching the span tag.')
            return 'Not found.'