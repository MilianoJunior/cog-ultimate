import pandas as pd
import json
import time
import httpx 
from models.config import leituras
import copy
import random
import asyncio
# from datetime import datetime
from collections import defaultdict
from datetime import datetime

# histórico compartilhado entre chamadas, como no seu código original
historico = defaultdict(dict)      # chave = "usina key - Enrolamento Fase A",   valor = { "12:20": 42.6, ... }


async def list_modbus_connections(config):
    """Lista todas as conexões Modbus ativas via API."""
    async with httpx.AsyncClient(verify=False, timeout=httpx.Timeout(5.0)) as client:
        try:
            response = await client.get(f"http://{config['ip']}:{config['port']}/listConnections")
            connections_data = response.json()
            if connections_data.get('status') != 'success':
                await close_modbus_connections(config)
                raise Exception(f"[ERRO API] {connections_data.get('message')}")
            return connections_data.get('data'), time.time()
        except Exception as e:
            await close_modbus_connections(config)
            raise Exception(f"[ERRO] {e}")
        
async def close_modbus_connections(config):
    """Fecha todas as conexões Modbus ativas via API."""
    async with httpx.AsyncClient(verify=False, timeout=httpx.Timeout(5.0)) as client:
        try:
            response = await client.post(f"http://{config['ip']}:{config['port']}/closeConnections")
            connections_data = response.json()
            if connections_data.get('status') != 'success':
                raise Exception(f"[ERRO API] {connections_data.get('message')}")
            return True
        except Exception as e:
            raise Exception(f"[ERRO] {e}")
        
def verify_all_connections():
    ''' Verifica se todas as conexões estão funcionando '''
    ips = {'APARECIDA':'100.110.212.125', 'FAE':'100.106.33.66','PICADAS':'100.79.241.13','PEDRAS':'100.93.237.40','HOPPEN':'100.73.37.105'}
    for key, value in ips.items():
        print(f"Verificando conexão: {key}")
        config = {'ip': value, 'port': 8010}
        data, timestamp = asyncio.run(list_modbus_connections(config))
        if len(data['active_connections']) != 0:
            asyncio.run(close_modbus_connections(config))
            print(f"Conexão {key} fechada")
        print(data)
        print(timestamp)
        print('-' * 50)
        time.sleep(5)

async def json_to_dataframe(json_data):
    data = dict(json_data)
    valores = {}
    for valor in data.values():
        for key, value in valor.items():
            valores[key] = value
    df = pd.DataFrame([valores])
    return df

def generate_data(body):
    import random
    registers = body['registers'].copy()
    for register in registers:
        if register == 'REAL':
            for key, value in registers[register].items():
                registers[register][key] = None
        elif register == 'INT':
            for key, value in registers[register].items():
                registers[register][key] = None
    return registers

def validate_data(data):
    if isinstance(data, pd.DataFrame):
        return True
    return False

async def get_data(config, data):
    '''config: dict {ip: str, port: int, tipo: str, unidade: str}
       data: dict {conexao: str, registers: dict}'''
    inicio = time.time()
    body = {
        "conexao": data['conexao'],
        "registers": data[config['tipo']]
    }    
    tipo = config['tipo'] if config['tipo'] != 'temperaturas' else 'leituras'
    # Definindo timeout de 3 segundos para a requisição
    timeout = httpx.Timeout(3.0)
    async with httpx.AsyncClient(verify=False, timeout=timeout) as client:
        try:
            response = await client.post(f"http://{config['ip']}:{config['port']}/readCLP/{tipo}", json=body)
            # print("##",5)
            # print('Query: ', f"http://{config['ip']}:{config['port']}/readCLP/{tipo}")
            # print(body)
            
            leituras_data = response.json()
            # print('leituras_data: ', leituras_data)
            # print("##",5)
            fim = time.time() - inicio
            if leituras_data['status'] == 'success':
                
                # print("##",5)
                return leituras_data['data'], fim
            else:
                # print('leituras_data: ', leituras_data)
                # print("##",5)
                return generate_data(body), fim
        except (httpx.TimeoutException, Exception) as e:
            print('Erro: ', e)
            fim = time.time() - inicio
            gerar_dados = generate_data(body)
            return gerar_dados, fim
        
async def set_data(cont, usina, config, data):
    '''config: dict {ip: str, port: int, tipo: str, unidade: str}
       data: dict {conexao: str, registers: dict}'''
    inicio = time.time()
    body = {
        "conexao": data['conexao'],
        "registers": data[config['tipo']]
    }    
    
    # Definindo timeout de 5 segundos para a requisição
    timeout = httpx.Timeout(3.0)
    async with httpx.AsyncClient(verify=False, timeout=timeout) as client:
        try:
            response = await client.post(f"http://{config['ip']}:{config['port']}/WriteCLP/{config['tipo']}", json=body)
            leituras_data = response.json()
            fim = time.time() - inicio
            if leituras_data['status'] == 'success':
                return leituras_data['data'], fim
            else:
                return generate_data(body), fim
        except (httpx.TimeoutException, Exception) as e:
            fim = time.time() - inicio
            gerar_dados = generate_data(body)
            return gerar_dados, fim
        
def safe_float(val):
    try:
        return float(val)
    except (TypeError, ValueError):
        return float('-inf')

def fetch_all_clp_data(select_type):
    usinas = leituras.keys()
    tasks = []
    clp_info = []
    for usina in usinas:
        config = {
            'ip': leituras[usina]['ip'],
            'port': leituras[usina]['port'],
            'table': leituras[usina]['table'],
            'tipo': select_type
        }
        data = leituras[usina]['CLPS']
        for key, value in data.items():
            tasks.append(get_data(config, value))
            clp_info.append((usina, key))
    results = asyncio.run(_gather_data(tasks))
    return clp_info, results

def enrich_clp_data(clp_info, results):
    response = []
    for (usina, key), (leitura, tempo) in zip(clp_info, results):
        for val in leitura.values():
            for k, v in val.items():
                response.append({
                    'title': f'{usina} {key}',
                    'key': k,
                    'value': v,
                    'tipo': 'kW',
                    'potencia_maxima': leituras[usina]['CLPS'][key]['caracteristicas']['potência máxima'],
                    'tempo': tempo
                })
    return response

def filter_and_sort(data, key_name):
    filtered = [line for line in data if line['key'] == key_name]
    sorted_data = sorted(
        filtered,
        key=lambda x: (x['value'] is None, safe_float(x['value'])),
        reverse=True
    )
    return sorted_data

def get_current_values(select_type):
    """
    Busca e organiza os valores atuais de todos os CLPs de todas as usinas.
    """
    clp_info, results = fetch_all_clp_data(select_type)
    response = enrich_clp_data(clp_info, results)
    potencias = filter_and_sort(response, 'Potência Ativa')
    # temperaturas = filter_and_sort(response, 'Temperatura')
    return response

async def _gather_data(tasks):
    return await asyncio.gather(*tasks) 



def enrich_temperaturas(clp_info, results, max_pontos=10):
    """
    clp_info :  sequência de tuplas (usina, key)
    results  :  sequência de tuplas (dicionário, tempo_execução)

    Retorna   :  lista de dicionários
    """
    saida      = []
    timestamp  = datetime.now().strftime('%H:%M')

    # percorre clp_info e results em paralelo
    for (usina, key), (leitura, t_exec) in zip(clp_info, results):
        dados_real = leitura.get('REAL', {})             # {'Enrolamento Fase A value': 42.6, ...}

        grupos = defaultdict(dict)                       # {'Enrolamento Fase A': {'value':42.6,'alarmes':90.0,'trip':110.0}, …}

        for campo_completo, valor in dados_real.items():
            base, sufixo = campo_completo.rsplit(' ', 1) # separa "… Fase A"  de  "value|alarmes|trip"
            grupos[base][sufixo] = round(valor, 2) if valor is not None else None

        # monta saída para cada grupo (Fase A, Fase B, Fase C…)
        for enrolamento, medidas in grupos.items():
            nome_ponto = f'{usina} {key} - {enrolamento}'

            # — Atualiza histórico —
            hist = historico[nome_ponto]
            hist[timestamp] = medidas.get('value')       # adiciona ponto da hora/minuto atual
            while len(hist) > max_pontos:                # mantém só os N mais recentes
                hist.pop(next(iter(hist)))

            # — Empacota resposta —
            saida.append({
                'nome'      : nome_ponto,
                'historico' : dict(hist),                # converte defaultdict→dict p/ evitar referências externas
                'atual'     : medidas.get('value'),
                'alarme'    : medidas.get('alarmes'),
                'trip'      : medidas.get('trip'),
            })

    return saida

def ordenar_por_proximidade_trip(leituras, incluir_risco=False):
    """
    Ordena a lista de dicionários (saída do enrich_temperaturas) pelo maior
    risco de atingir o valor de TRIP.

    Parâmetros
    ----------
    leituras : list[dict]
        Cada item deve conter pelo menos as chaves 'atual' e 'trip'.
    incluir_risco : bool, opcional
        Se True, acrescenta a chave 'risco' em cada item (0-100 %) antes de retornar.

    Retorna
    -------
    list[dict]
        Nova lista ordenada (do maior para o menor risco).
    """

    def calc_risco(item):
        try:
            # quociente atual/trip; se trip = 0 ou None → risco 0
            risco = item['atual'] / item['trip']
        except (KeyError, TypeError, ZeroDivisionError):
            risco = 0
        return risco

    # cria cópia ordenada (reverse=True → maior risco primeiro)
    ordenada = sorted(leituras, key=calc_risco, reverse=True)

    if incluir_risco:
        for item in ordenada:
            item['risco'] = round(calc_risco(item) * 100, 1)  # em %
    return ordenada


def get_temperaturas():
    # print('get_temperaturas')
    clp_info, results = fetch_all_clp_data('temperaturas')
    # print('clp_info: ', clp_info)
    # print('results: ', results)
    response = enrich_temperaturas(clp_info, results)
    response = ordenar_por_proximidade_trip(response, incluir_risco=True)
    # print('response: ', response)
    # temperaturas = filter_and_sort(response, 'Temperatura')
    # temperaturas_ordenadas = ordenar_temperaturas_por_alarme(response)
    # print('temperaturas ordenadas: ', temperaturas_ordenadas)
    return response

    # usinas = leituras.keys()
    # tasks = []
    # clp_info = []
    # for usina in usinas:
    #     config = {
    #         'ip': leituras[usina]['ip'],
    #         'port': leituras[usina]['port'],
    #         'table': leituras[usina]['table'],
    #         'tipo': 'temperaturas'
    #     }
    #     data = leituras[usina]['CLPS']
    #     for UG, value in data.items():
    #         print(' 2- Value: ', value.keys())
    #         print('--------------------------------------------------')
    #         # for k, v in value['temperaturas'].items():
    #         #     print(k, v)
    #             # for s, p in v.items():
    #             #     for t, m in p.items():
    #             #         print(f"'{s} {t}':{m},")
    #             # print(k, v.keys())
    #             # print(k, v.values())
    #             # print(k, v.values()['value'])
    #             # print(k, v.values()['alarmes'])
    #             # print(k, v.values()['trip'])
    #         print('--------------------------------')
    #         tasks.append(get_data(config, value))
    #         clp_info.append((usina, key))
    # results = asyncio.run(_gather_data(tasks))
    # return clp_info, results
    return get_temperaturas_fake()


def get_temperaturas_fake():
    import random
    mancais = [
        "CGH FAE - UG01 Mancal Guia",
        "CGH FAE - UG01 Mancal Escora",
        "CGH FAE - UG02 Mancal Guia", 
        "CGH FAE - UG02 Mancal Escora",
        "CGH FAE - UG03 Mancal Guia",
        "CGH FAE - UG03 Mancal Escora",
        "CGH FAE - UG04 Mancal Guia",
        "CGH FAE - UG04 Mancal Escora"
    ]
    
    temperaturas = []
    for nome in mancais:
        temperaturas.append({
            "nome": nome,
            "historico": {
                '12:20': random.randint(20, 50),
                '12:21': random.randint(20, 50),
                '12:22': random.randint(15, 45),
                '12:23': random.randint(25, 55),
                '12:24': random.randint(20, 50),
                '12:25': random.randint(18, 48),
                '12:26': random.randint(22, 52)
            },
            "atual": round(random.uniform(65.0, 75.0), 1),
            "alarme": round(random.uniform(55.0, 65.0), 1),
            "trip": round(random.uniform(65.0, 75.0), 1)
        })
    
    return temperaturas


def set_current_values(select_type):
    global leituras
    leituras_copy = copy.deepcopy(leituras)
    usinas = leituras_copy.keys()
    response = []
    cont = 0
    for usina in usinas:
        cont += 1
        ip = leituras_copy[usina]['ip']
        port = leituras_copy[usina]['port']
        tabela = leituras_copy[usina]['table']
        config ={
            'ip': ip,
            'port': port,
            'table': tabela,
            'tipo': select_type
        }
        data = leituras_copy[usina]['CLPS']
        for key, value in data.items():
            leitura, tempo = asyncio.run(set_data(cont,usina, config, value))
            for val in leitura.values():
                for k, v in val.items():
                    response.append({
                        'title': f'{usina} {key}',
                        'key': k,
                        'value': v,
                        'tipo': 'kVA',
                        'tempo': tempo
                    })
    return response

def get_usinas():
    usinas = leituras.keys()
    return list(usinas)



# incrementador_potencia =
# array_diferencial_grade = []

# array_diferencial_grade.append(diferencial_grade)



# media_diferencial_grade = sum(array_diferencial_grade) / len(array_diferencial_grade)



# if diferencial_grade > set_point and media_diferencial_grade > set_point:
    

#     incrementador_potencia -= 1
#     set_potencia = set_potencia +incrementador_potencia

# else:
#     incrementador_potencia += 1
#     set_potencia = set_potencia +incrementador_potencia

# if set_potencia > potencia_minima:
#     trip = True