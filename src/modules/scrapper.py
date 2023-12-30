import requests
import asyncio
from pandas import Series
from typing import Union, List
from bs4 import BeautifulSoup

def simple_distance_scrapper(origin: str, destination: str) -> Union[float, str, None]:
    """Function that scrap the distance of two cities from google using requests lib."""
    # ------------------------
    url = f'https://www.google.com/search?q=distância entre {origin} e {destination}'
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0'
    }
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

class Scrapper:
    def __init__(self, origin: Series, destination: Series):
        self.origin = origin
        self.destination = destination
    
    def _create_params(self) -> List:
        """Method to create the request parameters."""
        query_params = list()
        for origin, dest in zip(self.origin, self.destination):
            url = f'https://www.google.com/search?q=distância entre {origin} e {dest}'
            query_params.append(url)
        return query_params
    
    def _request_manager(self):
        s = requests.Session()