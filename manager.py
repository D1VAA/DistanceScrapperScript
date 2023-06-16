import asyncio
import time
import aiohttp
import pandas as pd

from itertools import zip_longest
from bs4 import BeautifulSoup
from packages.verifyColumns import verifyuf
from packages.managingProxy import proxyManager

length_batches = 10
url = 'https://www.google.com/search?'
estados = ['AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 'MT', 'MS', 'MG',
           'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN', 'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO']
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0'
}

params_dict = dict()
distances: dict[str, dict[str, float | int]] = dict()
htmls: dict[str, dict[str, str]] = dict()
best_distance: dict[str, dict[str, str]] = dict()


class Colors:
    NEUTRAL = '\033[0m'
    BG_RED = "\033[7;49;91m"
    RED = '\033[1;49;91m'
    CIAN = '\033[36m'
    ORANGE = '\033[33m'
    UND_RED = '\033[4;49;91m'
    BG_WHITESMOKE = '\033[7;49;97m'
    BG_WHITE = '\033[7;49;39m'
    GREEN = '\033[32m'


class ConsultaSheet:
    @verifyuf
    def __init__(self, option, sheet1, sheet2, colunaorigem, colunadestino, uforigem=None, ufdestino=None):
        self.option = option
        self.colunaOrigem = colunaorigem
        self.colunaDestino = colunadestino
        self.sheetOrigem = pd.read_excel(sheet1)
        self.sheetDestino = pd.read_excel(sheet2)

        self.ufOrigem = uforigem if uforigem is not None else ""
        self.ufDestino = ufdestino if ufdestino is not None else ""
        self.dataOrigem = self.sheetOrigem[[self.colunaOrigem, self.ufOrigem]]
        self.dataDestino = self.sheetDestino[[self.colunaDestino, self.ufDestino]]

    async def createparams(self):
        for _, row in self.dataOrigem.iterrows():
            for _, row2 in self.dataDestino.iterrows():
                origin = f"{row[self.colunaOrigem].title()} {row[self.ufOrigem]}"
                destiny = f'{row2[self.colunaDestino].title()} {row2[self.ufDestino]}'

                params = {
                    'q': f'distância entre {origin} e {destiny}'}

                if len(params_dict) < 1:
                    params_dict[f'{row[self.colunaOrigem]} x {row2[self.colunaDestino]}'] = params
                else:
                    if f'{row[self.colunaOrigem]} x {row2[self.colunaDestino]}' not in params_dict.keys():
                        params_dict[f'{row[self.colunaOrigem]} x {row2[self.colunaDestino]}'] = params

    @staticmethod
    async def dorequest(session, origem, destino, params, proxy=None):
        for _ in params:
            try:
                async with session.get(url, params=params, headers=headers, proxy=proxy) as response:
                    print(Colors.RED + f'{"BUSCANDO:"}' + Colors.NEUTRAL, end=" ")
                    print('Distância entre: ' + Colors.CIAN + f'{origem:^23} x {destino:^23}' + Colors.NEUTRAL)

                    status_code = response.status
                    if status_code == 429:
                        print(f'Response Code: {status_code} Too Many Requests')
                        print('\n\nAtivando Proxies para prosseguir...')
                        return 'useProxy'

                    html = await response.text()

                    if origem not in htmls.keys():
                        htmls[origem] = {}

                    elif destino not in htmls[origem]:
                        htmls[origem][destino] = html

            except Exception as e:
                print('Error', e)

    @staticmethod
    def scrapresponse():
        print('\n\n')
        print(Colors.BG_WHITE + f'{">" * 25} Extraindo Distâncias {"<" * 25}' + Colors.NEUTRAL)
        for origem, dhtmls in htmls.items():
            distances[origem] = {}
            for destino, html in dhtmls.items():
                soup = BeautifulSoup(html, 'html.parser')
                span = soup.find('span', class_='UdvAnf')
                try:
                    for item in span:
                        span_text = item.text
                        if 'km' in span_text:
                            km_str = span_text[:-3].replace(".", "").replace(",", ".")
                            distance = float(km_str)
                            distances[origem][destino] = distance
                            print(f"{origem:^21} x " + Colors.CIAN + f"{destino:^23}" + Colors.NEUTRAL, end=" ")
                            print("=> Distância: " + Colors.RED + f"{distance}" + Colors.NEUTRAL)

                except TypeError:
                    pass

    @staticmethod
    def verifydistance() -> None:
        print('\n\n')
        print(f"{Colors.BG_WHITESMOKE}{'>' * 25} Melhores Combinações {'<' * 25}{Colors.NEUTRAL}")
        for origem, destinos in distances.items():
            best_distance[origem] = {}
            borigem = best_distance[origem]

            for destino, km in destinos.items():
                if km == min(destinos.values()):
                    borigem[destino] = km
                    print(f'>> {origem:^23} {Colors.BG_RED}{"X":^3}{Colors.NEUTRAL} {Colors.CIAN}{destino:^23}',
                          end=" ")
                    print(f' {Colors.NEUTRAL}>>> {Colors.ORANGE}{km:^6}{Colors.NEUTRAL} km' + Colors.NEUTRAL)

    def exportxlsx(self):
        print(f'\n\n{Colors.BG_RED}Exporting...' + Colors.NEUTRAL)
        exp = pd.DataFrame()
        if self.option == 1:
            km = [km for km2 in best_distance.values() for km in km2.values()]
            uni_origin = [ori for ori in best_distance.keys()]
            uni_destiny = [dest for d in best_distance.values() for dest in d.keys()]
            exp['Origem'] = uni_origin
            exp['Destino'] = uni_destiny
            exp['Distância'] = km
        else:
            km = [km for km2 in distances.values() for km in km2.values()]
            destinations = [dest for d in distances.values() for dest in d.keys()]
            origins = [ori for ori in distances.keys() for _ in range(len(distances[ori].values()))]
            exp['Origem'] = origins
            exp['Destino'] = destinations
            exp['Distância'] = km

        exp.to_excel(r'./Result.xlsx')

    async def tasks_manager(self):
        async with aiohttp.ClientSession() as session:  # Start a session with aiohttp
            await self.createparams()
            params_dict_copy = params_dict.copy()
            batches = zip_longest(*[iter(params_dict_copy)] * length_batches)
            inicio = time.time()
            tasks = []

            for batch in batches:
                batch_items = [(x, params) for x, params in params_dict_copy.items() if x in batch]
                for x, params in batch_items:
                    origem = x.split('x')[0][:-1].title()  # Origin name formatted
                    destino = x.split('x')[-1][1:].title()  # Destination name formatted

                    tasks.append(asyncio.create_task(self.dorequest(session=session,
                                                                    origem=origem,
                                                                    destino=destino,
                                                                    params=params, )))

                await asyncio.gather(*tasks)

            fim = time.time()
            texec = fim - inicio
            print('\n')
            print(f'Requisições Feitas: ' + Colors.UND_RED + f'{len(tasks)}' + Colors.NEUTRAL, end=' ')
            print(f'=> Tempo de Execução: {Colors.UND_RED}{texec:.2f}' + Colors.NEUTRAL)

            self.scrapresponse()

            if self.option == 1:
                self.verifydistance()
                self.exportxlsx()
            else:
                self.exportxlsx()

    def compare(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.tasks_manager())
