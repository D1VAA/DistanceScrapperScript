import requests
from bs4 import BeautifulSoup
import pandas as pd

estados = ['AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN', 'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO']

def verifyUF(func):
    def wrapper(*args, **kwargs):
        if len(args) >= 6 and args[-2:] == (None, None):
            sheetOrigem = pd.read_excel(args[0])
            sheetDestino = pd.read_excel(args[1])
        
            colunaOrigem = args[2]
            colunaDestino = args[3]

            #Dados para consulta da planilha de Origem
            coluna_lado = sheetOrigem.columns.get_loc(colunaOrigem)+1
            coluna_lado_nome = sheetOrigem.columns[coluna_lado]
            estado_consulta = sheetOrigem.loc[0, coluna_lado_nome]
            
            #Dados para consulta da planilha de destino
            coluna_lado_destino = sheetDestino.columns.get_loc(colunaDestino)+1
            coluna_lado_nome_destino = sheetDestino.columns[coluna_lado_destino]
            estado_consulta_destino = sheetDestino.loc[0, coluna_lado_nome_destino]
            
            try:
                #Verifica a coluna da planilha de Origem
                if estado_consulta.upper() in estados:
                    args[4] = coluna_lado_nome

                #Verifica a coluna da planilha de destino
                if estado_consulta_destino.upper() in estados:
                    args[5] = coluna_lado_nome_destino

            except Exception as e:
                print(e)

        elif kwargs.get('ufOrigem') is None and kwargs.get('ufDestino') is None:
            sheetOrigem = pd.read_excel(kwargs['sheet1'])
            sheetDestino = pd.read_excel(kwargs['sheet2'])

            colunaOrigem = kwargs['colunaOrigem']
            colunaDestino = kwargs['colunaDestino']

            #Dados para consulta da planilha de Origem
            coluna_lado = sheetOrigem.columns.get_loc(colunaOrigem)+1
            coluna_lado_nome = sheetOrigem.columns[coluna_lado]
            estado_consulta = sheetOrigem.loc[0, coluna_lado_nome]
            cidade_consulta = sheetOrigem.loc[0, colunaOrigem]
            
            #Dados para consulta da planilha de destino
            coluna_lado_destino = sheetDestino.columns.get_loc(colunaDestino)+1
            coluna_lado_nome_destino = sheetDestino.columns[coluna_lado_destino]
            estado_consulta_destino = sheetDestino.loc[0, coluna_lado_nome_destino]
            cidade_consulta_destino = sheetDestino.loc[0, colunaDestino]
            
            try:
                #Verifica a coluna da planilha de Origem
                if estado_consulta.upper() in estados:
                    kwargs['ufOrigem'] = coluna_lado_nome

                #Verifica a coluna da planilha de destino
                if estado_consulta_destino.upper() in estados:
                    kwargs['ufDestino'] = coluna_lado_nome_destino


            except Exception as e:
                print('Error: ',e)

        return func(*args, **kwargs)

    return wrapper
