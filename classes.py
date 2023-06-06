import asyncio
import time
from itertools import zip_longest

import aiohttp
import pandas as pd
from bs4 import BeautifulSoup
from decorators.headers import randomHeader
from decorators.stringfy import stringfyParams
from decorators.verifyColumns import verifyUF

length_batches = 3
url = 'https://www.google.com/search?'
estados = ['AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 'MT', 'MS', 'MG',
           'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN', 'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO']

params_dict = dict()
htmls = dict()
best_distance = dict()

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
    @stringfyParams
    @verifyUF
    def sheets(self, sheet1, sheet2, colunaOrigem, colunaDestino, ufOrigem=None, ufDestino=None):
        self.colunaOrigem = colunaOrigem
        self.colunaDestino = colunaDestino
        self.sheetOrigem = pd.read_excel(sheet1)
        self.sheetDestino = pd.read_excel(sheet2)

        self.ufOrigem = ufOrigem if ufOrigem is not None else ""
        self.ufDestino = ufDestino if ufDestino is not None else ""
        self.dataOrigem = self.sheetOrigem[[self.colunaOrigem, self.ufOrigem]]
        self.dataDestino = self.sheetDestino[[self.colunaDestino, self.ufDestino]]


    #Cria os parâmetros das requests.
    async def createParams(self):
        for i, row in self.dataOrigem.iterrows():
            for j, row2 in self.dataDestino.iterrows():
                params = {'q': f'distância entre {row[self.colunaOrigem]} {row[self.ufOrigem]} e {row2[self.colunaDestino]} {row2[self.ufDestino]}'}

                if len(params_dict) < 1:
                    params_dict[f'{row[self.colunaOrigem]} x {row2[self.colunaDestino]}'] = params
                else:
                    if f'{row[self.colunaOrigem]} x {row2[self.colunaDestino]}' not in params_dict:
                        params_dict[f'{row[self.colunaOrigem]} x {row2[self.colunaDestino]}'] = params


    @randomHeader
    async def doRequest(self, session, origem, destino, params, headers=None):
        for itens in params:
            try:
                async with session.get(url, params=params[itens], headers=headers) as response:
                    print(f'\033[1;49;91m{"BUSCANDO:"}\033[0m Distância entre: \033[36m{origem:^23} x {destino:^23}\033[0m')
                    status_code = response.status
                    if status_code == 429:
                        print(status_code)
                        return 'closeSession'

                    html = await response.text()

                    if origem not in htmls.keys():
                       htmls[origem] = {}

                    elif destino not in htmls[origem]:
                        htmls[origem][destino] = html

            except Exception as e:
                print('Error', e)


    async def scrapResponse(self):
        self.distances = dict()
        print(f'{">"*10}Extraindo Distâncias{"<"*10}')
        for origem, destino in htmls.items():
            for html in destino.values(): 
                soup = BeautifulSoup(html, 'html.parser');
                span = soup.find_all('span', class_='UdvAnf')
                for item in span:
                    distance = float(item.text[:-3].replace(".", "").replace(",", ".")) if 'km' in item.text else None
                    self.distances[origem][destino] = distance  
                    print(f"Rota: Origem{origem} x {destino} : {distance}")



        await self.verifyDistance()

    async def verifyDistance(self):
        best_distance = dict();

        for origem, destino in self.distances:
            best_distance[origem] = {}

            for d in destino:
                actual_d = self.distances[origem][d]
                actual_origin = best_distance[origem]

                if len(actual_origin < 1):
                    actual_origin[d] = actual_d

                else:
                    if min(actual_origin.values() > actual_d):
                        actual_origin = {d: actual_d}


async def main():
    consulta = ConsultaSheet()
    consulta.sheets(sheet1='TABELA_FARINHA.xlsx', sheet2='DESTINOS_PLACAS_SOLARES.xlsx', colunaOrigem='Origem', colunaDestino='Destino')
        #Start a session with aiohttp and send this session to doRequest() method
    async with aiohttp.ClientSession() as session:
        await consulta.createParams()
        params_dict_copy = params_dict.copy()
        batches = zip_longest(*[iter(params_dict_copy)] * length_batches)
        inicio = time.time()
        tasks = []

        for batch in batches:
            batch_items = [(x, params) for x, params in params_dict_copy.items() if x in batch]
            for x, params in batch_items:
                origem = x.split('x')[0][:-1] #Origin name formatted
                destino = x.split('x')[-1][1:] #Destination name formatted

                tasks.append(asyncio.create_task(consulta.doRequest(session=session, origem=origem, destino=destino, params=params))) # Tasks for asyncio
            await asyncio.gather(*tasks)

        fim = time.time()
        print('Requisições Feitas: ', len(tasks), 'Tempo de Execução: ', fim-inicio)
    await consulta.scrapResponse()


loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
loop.run_until_complete(main())
