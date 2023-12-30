from typing import Any

import pandas as pd
import aiohttp
import asyncio
import aiohttp_socks
from time import time

data = pd.read_json('./packages/Free_Proxy_List.json')
data['anonimityLevel'] = 'elite'
data = data[data.protocols != 'https']
sort_responses = data.sort_values(by='responseTime')
response_times = dict()


class Colors:
    NEUT = '\033[0m'
    BG_RED = "\033[7;49;91m"
    RED = '\033[1;49;91m'
    CIAN = '\033[36m'
    ORANGE = '\033[33m'
    UND_RED = '\033[4;49;91m'
    BG_WHITESMOKE = '\033[7;49;97m'
    BG_WHITE = '\033[7;49;39m'
    GREEN = '\033[32m'


async def managingProxy():
    """
    Function to bypass 429 response code (Too Many Requests) using proxy.
    If useTor set to True, the function will start proxy server and return the
    default tor proxy_url:'socks5://127.0.0.1:9050'
    The 'tests' parameter determines how many of the best free proxy serves will be tested to determine the best.
    Default=5
    """

    def createProxyList() -> dict:  # Função para fazer uma lista com os proxies que serão testados
        test_proxies_dict = dict()
        test = len(data['ip'])
        for line in range(test):
            protocol = sort_responses.loc[line, 'protocols'][0]  # Seleciona o protocolo
            ip_address = sort_responses.loc[line, 'ip']  # Seleciona o ip 
            port = sort_responses.loc[line, 'port']  # Seleciona a porta

            proxy = f'{protocol}://{ip_address}:{port}'  # Monta o url do proxy
            test_proxies_dict[line] = proxy  # Acrescenta a url do proxy a um dicionário

        return test_proxies_dict  # Retorna o dicionário com as urls que serão testadas

    async def connectionTest(proxy_url, connector, cont) -> None:  # Função para testar a conexão dos proxies
        """
        :type proxy_url: url
        :type cont: int
        :type connector: BaseConnector | None
        """
        print(Colors.CIAN + 'Proxy Nº:  ' + Colors.NEUT + f'{cont + 1} >>>', end=" ")
        print(Colors.GREEN + 'Proxy Url: ' + Colors.RED + f'{proxy_url}' + Colors.NEUT)

        try:
            # Start a session with the proxy url and make a request at the google
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.get('https://www.google.com/') as response:
                    inicio = time()
                    # Captura o tempo que demora para receber a resposta
                    await response.text()

                    if response.status == 200:
                        fim = time()
                        r_time = fim - inicio
                        response_times[proxy_url] = r_time
                        print(f'\n\nTempo de resposta do Proxy: {proxy_url} = {r_time} segundos')

                    else:
                        print('Erro: ', response.status)

        except (aiohttp.ClientError, asyncio.TimeoutError, aiohttp.ClientConnectionError, ConnectionResetError):
            print(f'Proxy Nº {cont} Tentativa de conexão mal sucedida...')
            return

    async def managingCoro() -> str | None:
        tasks = list()  # Lista vazia que terá as tasks do asyncio
        proxies_list = createProxyList()  # Lista de proxys formada a partir do arquivo json

        try:
            for cont, url in proxies_list.items():
                connector = aiohttp_socks.ProxyConnector.from_url(url)
                tasks.append(connectionTest(url, connector, cont))

            # Wait until all tasks end the execution
            await asyncio.gather(*tasks)

        # Any exception will be printed
        except Exception as e:
            print(e)

        # If found valid results, it will be printed
        print(response_times)
        if len(response_times) != 0:
            print(
                Colors.BG_RED + f"{len(response_times)} resultados válidos encontrados.\n{response_times}" + Colors.NEUT
            )
            best_connection = []  # List for filter the best option
            for url, time in response_times.items():
                if time == min(response_times.values()):
                    best_connection.append(url)
                    return best_connection[0]  # Return the lower value

        else:  # Bloco else para o caso de nenhum proxy ter conseguido conectar
            print(f"Sem resultados válidos encontrados...")
            alt = input("Deseja usar o Tor ? [S/N]: ")

            if alt.upper() == 'S':
                print('Gentileza inciar o serviço manualmente...')
                input("\n\nServiço iniciado? [S/N]")
                return 'socks5://127.0.0.1:9050'

            else:
                print('Encerrando...')
                return 'Stop'

    result = await managingCoro()  # Aguarda e salva o resultado da execução da função managingCoro
    return result  # Retornar o resultado da função managingCoro


async def proxyManager():
    result = await managingProxy()
    return result
