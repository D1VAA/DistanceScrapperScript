import pandas as pd

estados = ['AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI',
           'RJ', 'RN', 'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO']


def verifyuf(func):
    def wrapper(*args, **kwargs):
        # Verifica se são 6 ou mais parametros e se os ultimos dois estão com o valor None
        if len(args) >= 6 and args[-2:] == (None, None):
            args = list(args)
            sheetorigem = pd.read_excel(args[0])  # Path para a planilha que contém as cidade de origem 
            sheetdestino = pd.read_excel(args[1])  # Path para a planilha que contém as cidade de destino

            colunaorigem = args[2]  # Nome da coluna que possui as cidades de origem
            colunadestino = args[3]  # Nome da coluna que possui as cidades de destino

            # Dados para consulta da planilha de Origem
            coluna_lado = sheetorigem.columns.get_loc(colunaorigem) + 1  # Pega a posição da coluna do lado
            coluna_lado_nome = sheetorigem.columns[coluna_lado]  # Pega o nome dessa coluna do lado
            estado_consulta = sheetorigem.loc[0, coluna_lado_nome]  # Pega o primeiro valor da coluna possivelmente UF

            # Dados para consulta da planilha de destino
            coluna_lado_destino = sheetdestino.columns.get_loc(colunadestino) + 1  # Pega a posição da coluna ao lado
            coluna_lado_nome_destino = sheetdestino.columns[coluna_lado_destino]
            estado_consulta_destino = sheetdestino.loc[0, coluna_lado_nome_destino]

            try:
                # Verifica se o valor pego na coluna possivelmente UF é um estado.
                if estado_consulta.upper() in estados:
                    args[4] = coluna_lado_nome

                # Verifica se o valor pego na coluna possivelmente UF é um estado.
                if estado_consulta_destino.upper() in estados:
                    args[5] = coluna_lado_nome_destino

            except Exception as e:
                print(e)

        elif kwargs.get('uforigem') is None and kwargs.get('ufdestino') is None:
            sheetorigem = pd.read_excel(kwargs['sheet1'])
            sheetdestino = pd.read_excel(kwargs['sheet2'])

            colunaorigem = kwargs['colunaorigem']
            colunadestino = kwargs['colunadestino']

            # Dados para consulta da planilha de Origem
            coluna_lado = sheetorigem.columns.get_loc(colunaorigem) + 1
            coluna_lado_nome = sheetorigem.columns[coluna_lado]
            estado_consulta = sheetorigem.loc[0, coluna_lado_nome]

            # Dados para consulta da planilha de destino
            coluna_lado_destino = sheetdestino.columns.get_loc(colunadestino) + 1
            coluna_lado_nome_destino = sheetdestino.columns[coluna_lado_destino]
            estado_consulta_destino = sheetdestino.loc[0, coluna_lado_nome_destino]

            try:
                # Verifica a coluna da planilha de Origem
                if estado_consulta.upper() in estados:
                    kwargs['uforigem'] = coluna_lado_nome

                # Verifica a coluna da planilha de destino
                if estado_consulta_destino.upper() in estados:
                    kwargs['ufdestino'] = coluna_lado_nome_destino

            except Exception as e:
                print('Error: ', e)

        return func(*args, **kwargs)

    return wrapper