import requests
import asyncio
from dataclasses import dataclass
from pandas import Series
from typing import Union, List, Optional
from bs4 import BeautifulSoup

headers = {
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0'
}
google_url = f'https://www.google.com/search?q=distância entre '

def simple_distance_scrapper(origin: str, destination: str) -> Union[float, str, None]:
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
    url: Optional[str] = None
    distance: Union[float, str, None] = None

class Scrapper:
    def __init__(self, origin: Series, destination: Series):
        self.origin = origin
        self.destination = destination
    
    def _create_querys(self) -> List[Route]:
        """Method to create a list with all the urls."""
        query_list = list()
        for origin, dest in zip(self.origin, self.destination):
            string = f'{origin} e {dest}'
            url = f'{google_url}{string}'
            query_list.append(Route(origin, dest, url=url))
        return query_list
    
    async def _request_manager(self) -> None:
        s = requests.Session()
        tasks = []
        for route in self._create_querys():
            task = asyncio.create_task(self._requester(s, route.url))
            tasks.append(task)
            distance = self._parser(response)

    @staticmethod
    async def _requester(session, url):
        session.get(url, headers=headers) 
        return await session.text

    @staticmethod
    def _parser(html) -> Union[float, str]:
        soup = BeautifulSoup(html, 'html.parser')
        span = soup.find('span', class_='UdvAnf')
        for item in span:  # type: ignore
            span_text = item.text  # type: ignore
            if 'km' in span_text:
                km_str = span_text[:-3].replace(".", "").replace(",", ".")
                km = float(km_str)
                return km
        return 'Distância não encontrada.'
    