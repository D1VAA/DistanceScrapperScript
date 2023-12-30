import asyncio
import time
import aiohttp
import pandas as pd

from itertools import zip_longest
from bs4 import BeautifulSoup
from packages.verifyColumns import verifyuf

url = 'https://www.google.com/search?'
estados = ['AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 'MT', 'MS', 'MG',
           'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN', 'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO']
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0'
}

params_dict = dict()
distances: dict[str, dict[str, float | int]] = dict()
best_distance: dict[str, dict[str, str]] = dict()

class Colors:
    N = '\033[0m'
    BG_RED = "\033[7;49;91m"
    RED = '\033[1;49;91m'
    CIAN = '\033[36m'
    BLUE = '\033[1;49;34m'
    ORANGE = '\033[1;49;33m'
    UND_RED = '\033[4;49;91m'
    BG_WHITESMOKE = '\033[7;49;97m'
    BG_WHITE = '\033[7;49;39m'
    GREEN = '\033[1;49;32m'
    BG_GREEN = '\033[7;49;32m'


class ConsultaSheet:
    @verifyuf
    def __init__(self,
                 option,
                 sheet1,
                 sheet2,
                 colunaorigem,
                 colunadestino,
                 uforigem=None,
                 ufdestino=None,
                 batchsize=2):
        self.option = option
        self.htmls = dict()
        self.length_batches = batchsize
        self.colunaOrigem = colunaorigem
        self.colunaDestino = colunadestino
        self.contador = 0
        self.sheetOrigem = pd.read_excel(sheet1)
        self.sheetDestino = pd.read_excel(sheet2)
        self.ufOrigem = uforigem
        self.ufDestino = ufdestino

        self.dataOrigem = self.sheetOrigem[[self.colunaOrigem, self.ufOrigem]] \
            if self.ufOrigem is not None else self.sheetOrigem[[self.colunaOrigem]]

        self.dataDestino = self.sheetDestino[[self.colunaDestino, self.ufDestino]] \
            if self.ufDestino is not None else self.sheetDestino[[self.colunaDestino]]

    async def createparams(self):
        if self.option == 1:
            for _, row in self.dataOrigem.iterrows():
                for _, row2 in self.dataDestino.iterrows():
                    origem = row[self.colunaOrigem]
                    destino = row2[self.colunaDestino]
                    ufori = row[self.ufOrigem] if self.ufOrigem is not None else ''
                    ufdest = row2[self.ufDestino] if self.ufDestino is not None else ''
                    params = {'q': f'distância entre {origem} {ufori} e {destino} {ufdest}'}

                    if f'{origem} x {destino}' not in params_dict.keys():
                        params_dict[f'{origem} x {destino}'] = [params]
                    elif f'{origem} x {destino}' not in params_dict.keys():
                        params_dict[f'{origem} x {destino}'] = [params]

        if self.option == 2:
            for (i, row), (_, row2) in zip(self.sheetOrigem.iterrows(), self.sheetDestino.iterrows()):
                origem = row[self.colunaOrigem]
                destino = row2[self.colunaDestino]
                ufori = row[self.ufOrigem] if self.ufOrigem is not None else ''
                ufdest = row2[self.ufDestino] if self.ufDestino is not None else ''
                param = {'q': f'distância entre {origem} {ufori} e {destino} {ufdest}'}

                if f'{origem} x {destino}' not in params_dict.keys():
                    params_dict[f'{origem} x {destino}'] = [param]
                elif f'{origem} x {destino}' in params_dict.keys():
                    params_dict[f'{origem} x {destino}'].append(param)

    async def dorequest(self, session, origem, destino, params):
        for param in params:
            try:
                async with session.get(url, params=param, headers=headers) as response:
                    print(f'{Colors.BLUE}|{Colors.N}', end=" ")
                    print(f'{origem:^23} {Colors.RED}[x]{Colors.N} {destino:^23}{Colors.BLUE}|{Colors.N}')
                    response.raise_for_status()
                    html = await response.read()

                    if origem not in self.htmls.keys():
                        self.htmls[origem] = {}

                    if destino not in self.htmls[origem].keys():
                        self.htmls[origem][destino] = html
            except Exception as e:
                print('Error', e)

        self.contador += 1

    def scrapresponse(self):
        print('\n\n')
        print(Colors.BG_WHITE + f'{">" * 25} Extraindo Distâncias {"<" * 25}' + Colors.N)
        for origem, dhtmls in self.htmls.items():
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
                            print(f"{origem:^21} x {Colors.CIAN}{destino:^23}{Colors.N}", end=" ")
                            print(f"=> Distância: {Colors.RED}{distance}{Colors.N}")

                except TypeError:
                    pass

    @staticmethod
    def verifydistance() -> None:
        print('\n\n')
        print(f"{Colors.BG_WHITESMOKE}{'>' * 25} Melhores Combinações {'<' * 25}{Colors.N}")
        for origem, destinos in distances.items():
            best_distance[origem] = {}
            borigem = best_distance[origem]

            for destino, km in destinos.items():
                if km == min(destinos.values()):
                    borigem[destino] = km
                    print(f'>> {origem:^23} {Colors.BG_RED}{"X":^3}{Colors.N} {Colors.CIAN}{destino:^23}',
                          end=" ")
                    print(f' {Colors.N}>>> {Colors.ORANGE}{km:^6}{Colors.N} km' + Colors.N)

    def exportxlsx(self):
        print(f'\n\n{Colors.GREEN}[*]{Colors.N} Exporting {Colors.GREEN}[*]{Colors.N}')
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
        print(f'{Colors.ORANGE}[*]{Colors.N} Exported  {Colors.ORANGE}[*]{Colors.N}\n\n')

    async def tasks_manager(self):
        async with aiohttp.ClientSession() as session:  # Start a session with aiohttp
            await self.createparams()
            params_dict_copy = params_dict.copy()
            batches = zip_longest(*[iter(params_dict_copy)] * self.length_batches)
            inicio = time.time()
            tasks = []

            print('\n\n')
            for batch in batches:
                batch_items = [(x, params) for x, params in params_dict_copy.items() if x in batch]
                for x, params in batch_items:
                    origem = x.split('x')[0][:-1].title()  # Origin name formatted
                    destino = x.split('x')[-1][1:].title()  # Destination name formatted
                    tasks.append(asyncio.create_task(self.dorequest(session=session,
                                                                    origem=origem,
                                                                    destino=destino,
                                                                    params=params)))
                    await asyncio.sleep(2)
                await asyncio.gather(*tasks)

            fim = time.time()
            texec = fim - inicio
            print('\n')
            print(f'Requisições Feitas: ' + Colors.UND_RED + f'{self.contador}' + Colors.N, end=' ')
            print(f'=> Tempo de Execução: {Colors.UND_RED}{texec:.2f}' + Colors.N)

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
