from typing import Union
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