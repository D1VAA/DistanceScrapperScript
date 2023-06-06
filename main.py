import requests
from bs4 import BeautifulSoup
import pandas as pd
from time import sleep
import asyncio

# Site e User-Agent para fazer a busca pelas distâncias.
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
url = 'https://www.google.com/search?'

#Abrindo as duas planilhas
sheet_farinha = pd.read_excel('./TABELA_FARINHA.xlsx')
sheet_destinos_placas = pd.read_excel('./DESTINOS_PLACAS_SOLARES.xlsx')

#Selecionando todos os dados das colunas necessárias.
dataOrigem = sheet_farinha[['Origem','UF2']]
dataDestino = sheet_farinha[['Destino']]
dataDestinos = sheet_destinos_placas[['Destino','UF']]

#Lista para o loop fazer o teste das distâncias e descobrir a cidade com a menor distância
teste_cidades_proximas = list()
params_dict = dict()

#Dicionário com as cidades de destino das placas solares que são próximas as origens da planilha de farinha
dict_cidades = dict()
cidade_mais_proxima = dict()

#Loop que roda por cada cidade da planilha de origem da planilha de farinha de osso e por cada cidade da planilha de destinos das 
# placas solares e relaciona elas formando um modelo de parâmetro que será passado dentro do request para conseguir a distãncia entre essas duas cidades.
async def createParams():
    for i, row in dataOrigem.iterrows():
        for j, row2 in dataDestinos.iterrows():
            params = {'q':f'distância entre {row["Origem"]} {row["UF2"]} e {row2["Destino"]} {row2["UF"]}'}

            if len(params_dict) < 1:
                params_dict[f'{row["Origem"]} x {row2["Destino"]}'] = params;
            else:    
                if f'{row["Origem"]} x {row2["Destino"]}' not in params_dict:
                    params_dict[f'{row["Origem"]} x {row2["Destino"]}'] = params;
                
#Loop que passará por todos os parâmetros salvos no dicionário e irá realizar os requests.
async def makeRequest():
    for itens in params_dict:
        try: 
            r = requests.get(url, params=params_dict[itens], headers=headers)
            soup = BeautifulSoup(r.content, 'html.parser')
            span_element = soup.find('span', class_='UdvAnf')
            #Encontra a informação do KM que está presenta no elemento "SPAN" do HTML
            for span in span_element:
                kmTexto = span.text;
                if "km" in kmTexto:
                    novoKm = kmTexto[:-3].replace(".", "").replace(",", ".")
                    distKm = float(novoKm)
                    
                    #Adciona o KM no dicionário "dict_cidades"
                    if itens.split("x")[0][:-1] not in dict_cidades:
                        print(f'\nORIGEM SELECIONADA: \033[7;49;91m{itens.split("x")[0][:-1]}\033[0m', end='\n\n')
                        dict_cidades[itens.split("x")[0][:-1]] = {}
                        await asyncio.sleep(2)
                    if itens.split("x")[-1][1:] not in dict_cidades[itens.split("x")[0][:-1]]:
                        dict_cidades[itens.split("x")[0][:-1]][itens.split("x")[-1][1:]] = distKm
                        await asyncio.sleep(2)
            print(f'\033[1;49;91m{"PESQUISANDO:"}\033[0m \033[36m{itens.split("x")[1]:<25}\033[0m Distância: \033[33m{distKm} km\033[0m')
        #Quando não encontrar resulatdo na pesquisa, irá retornar "Não Enontrado"
        #Quando a cidade de destino for a mesma de origem, será adicionado o valor de 0 km 
        except Exception as e:
            print(e)
            if itens.split("x")[0][:-1] == itens.split("x")[-1][1:].upper():
                print(f'\033[1;49;91m{"PESQUISANDO:"}\033[0m \033[36m{itens.split("x")[1]:<25}\033[0m Distância: \033[33m0 km\033[0m')
                dict_cidades[itens.split("x")[0][:-1]][itens.split("x")[-1][1:]] = 0
            else:
                print(f'\033[1;49;91m{"PESQUISANDO:"}\033[0m \033[36m{itens.split("x")[1]:<25}\033[0m ==> \033[33mNão Encontrado..\033[0m') 
    
""" Irá iterar pelos itens do dicionário 'dict_cidades' e passar apenas as cidades mais próximas 
para o dicionário 'cidade_mais_próxima' Modelo: {"ORIGEM":{"DESTINO1":"DISTANCIA1",'DESTINO2':'DISTÂNCIA2'}} """
async def verifyDistance():
    for origens, destinos in dict_cidades.items(): # 
        #Para cada origem, ele adiciona uma chave principal no dicionário MODELO: {"ORIGEM":{}}
        cidade_mais_proxima[origens] = {}
        for j in destinos:
            #Se a chave principal ainda não tiver valor atribuido, ele irá adicionar a primeira cidade e sua respectiva distância MODELO: {"ORIGEM":{"DESTINO1":"DISTÂNCIA1"}}
            if len(cidade_mais_proxima[origens]) < 1:
                cidade_mais_proxima[origens][j] = dict_cidades[origens][j]        
            else:
            #Se já tiver valor atribuido, vai verificar se o valor atual é menor do que o que já está no dicionário, se for, aquele será substituido pelo atual.
                if min(cidade_mais_proxima[origens].values()) > dict_cidades[origens][j]:
                    cidade_mais_proxima[origens] = {j: dict_cidades[origens][j]}

#Seção para mostrar os resultados, as cidades destinos mais próximas para as origens pesquisadas.
print(f'\n\n\033[4;49;91m{">"*20}\033[0m MELHORES COMBINAÇÕES \033[4;49;91m{"<"*20}\033[0m\n\n')
for i, j in cidade_mais_proxima.items():
    print(f'\033[36m{i:^21} x \033[32m{list(cidade_mais_proxima[i])[0]:^20}\033[0m => Distância \033[1;49;91m{cidade_mais_proxima[i][list(cidade_mais_proxima[i])[0]]} km\033[0m')

#Insere duas colunas na planilha com as rotas de origem pesquisadas.
#'Destinio_Placas' será preenchida com as cidades destino que são mais próximas.
sheet_farinha.insert(1, 'Destino_Placas',"")
#Distância será preenchida com a distância para a cidade mais próxima.
sheet_farinha.insert(1,"Distância","")

#Seção que irá preencher a planilha.
print(f'\n\n\\\033[4;49;91m{">"*20}\033[0m PREENCHENDO PLANILHA \033[4;49;91m{"<"*20}\033[0m', end='\n\n')

#Loop para iterar por cada origem da planilha e preencher cada linha com a cidade mais próxima e a sua distância.
for j, row in dataOrigem.iterrows():
    cidadesOrigem = row["Origem"]
    for origens, destinos in cidade_mais_proxima.items():
        if cidadesOrigem == origens:
            print(f"\033[0mLinha: \033[1;49;35m{j:<4}\033[0m Origem: \033[7;49;39m{cidadesOrigem:^25}\033[0m \033[0mDestino + Próximo:\033[0m \033[7;49;97m{list(destinos)[0]:^25}\033[0m", end=' ')
            print(f'=> Distância: \033[1;49;91m{list(cidade_mais_proxima[origens].values())[0]}\033[0m')
            sheet_farinha.loc[j, 'Destino_Placas'] = list(destinos)[0]
            sheet_farinha.loc[j, "Distância"] = list(cidade_mais_proxima[origens].values())[0]

sheet_farinha.to_excel('teste.xlsx', index=False)

async def main():
    await createParams()
    await makeRequest()
    await verifyDistance()

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
