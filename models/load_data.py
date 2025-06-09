import pandas as pd
import json
import time
import httpx 
from models.config import leituras
import copy
import random
import asyncio

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
    # Definindo timeout de 3 segundos para a requisição
    timeout = httpx.Timeout(3.0)
    async with httpx.AsyncClient(verify=False, timeout=timeout) as client:
        try:
            response = await client.post(f"http://{config['ip']}:{config['port']}/readCLP/{config['tipo']}", json=body)
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
                    'tipo': 'kVA',
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
    temperaturas = filter_and_sort(response, 'Temperatura')
    return potencias, temperaturas

async def _gather_data(tasks):
    return await asyncio.gather(*tasks) 


def get_temperaturas(select_type):
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

