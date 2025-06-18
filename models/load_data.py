import pandas as pd
import json
import time
import httpx 
from models.config import leituras
import copy
import random
import asyncio
from collections import deque # Added import
# time is already imported

# Global store for temperature history
temperature_history = {} # Key: (usina_id, unidade_id, temp_point_name), Value: deque(maxlen=20)
MAX_HISTORY_POINTS = 20

# --- Criteria for Attention Events ---
RATE_OF_CHANGE_THRESHOLD = 2.0  # Degrees Celsius per minute
PROXIMITY_PERCENTAGE_THRESHOLD = 10.0  # Percentage below alarm threshold

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

def enrich_clp_data(clp_info, results, select_type_of_data_fetched): # Added select_type
    response = []
    current_timestamp = time.time()

    for (usina_id, unidade_id), (clp_response_data, time_taken) in zip(clp_info, results):
        if not isinstance(clp_response_data, dict):
            logger_alarms.warning(f"Dados inesperados recebidos de get_data para {usina_id}/{unidade_id} (tipo {select_type_of_data_fetched}): {clp_response_data}")
            continue

        # Example: clp_response_data might be {'REAL': {'Enrolamento Fase A': 75.5, ...}}
        # or {'BOOLEAN': {'Alarme X': True, ...}}

        # This function is currently used for 'leituras' (Potência Ativa) and 'alarmes'.
        # We are now adding handling for 'temperaturas' specifically for history.

        if select_type_of_data_fetched == 'temperaturas':
            # Data comes typically under a 'REAL' key from get_data if it's from 'temperaturas' section
            real_values = clp_response_data.get('REAL', {})
            for temp_point_name, temp_value in real_values.items():
                # temp_point_name is like "Enrolamento Fase A"
                # temp_value is the actual temperature float

                # Store in history
                history_key = (usina_id, unidade_id, temp_point_name)
                if history_key not in temperature_history:
                    temperature_history[history_key] = deque(maxlen=MAX_HISTORY_POINTS)

                if temp_value is not None: # Only store valid readings
                    temperature_history[history_key].append((current_timestamp, temp_value))
                    logger_alarms.debug(f"Histórico de temperatura atualizado para {history_key}: {temp_value}")

                # Also, add to the 'response' list if CardTemperature or other components expect it directly from here.
                # This part needs to align with how get_temperaturas() will eventually source its data.
                # For now, get_current_values filters 'Temperatura' from this generic response.
                # The structure for 'Temperatura' points might need to be more specific if CardTemperature expects it.
                # The current 'response' structure is flat: {'key': 'Enrolamento Fase A', 'value': 75.5 ...}
                # This is okay if 'Enrolamento Fase A' is unique enough.

                # Check if this point is a 'value' register from the temperatures config
                # This ensures we only add actual temperature measurement points to the generic response list this way.
                # Status bits (alarm_config, trip_config registers) if read via 'temperaturas' type (if they were REAL)
                # would also come here. We only want points that have a 'value' sub-key in config.

                unit_clp_config = leituras.get(usina_id, {}).get('CLPS', {}).get(unidade_id, {})
                temp_point_config = unit_clp_config.get('temperaturas', {}).get('REAL', {}).get(temp_point_name)

                if temp_point_config and 'value' in temp_point_config: # This confirms it's a main temperature point
                    response.append({
                        'title': f'{usina_id} {unidade_id}', # For consistency with how Potencia Ativa is named
                        'key': temp_point_name, # e.g., "Enrolamento Fase A"
                        'value': temp_value,
                        'tipo': '°C', # Assuming Celsius
                        # 'potencia_maxima' is not applicable here, but other cards might expect a similar field.
                        # For CardTemperature, it expects 'alarme' and 'trip' thresholds.
                        'tempo': time_taken
                    })

        elif select_type_of_data_fetched == 'leituras': # Potencia Ativa, etc.
            # This is the original logic for 'leituras'
            for data_type_key, registers_dict in clp_response_data.items(): # e.g., data_type_key is 'INT' or 'REAL'
                if isinstance(registers_dict, dict):
                    for register_name, register_value in registers_dict.items():
                        # potencia_maxima is specific to 'Potência Ativa' typically.
                        # Need to ensure this is correctly sourced if 'leituras' handles more than just Potencia.
                        pot_max_val = None
                        try:
                            pot_max_val = leituras[usina_id]['CLPS'][unidade_id]['caracteristicas']['potência máxima']
                        except KeyError:
                            # logger_alarms.debug(f"Caracteristica 'potência máxima' não encontrada para {usina_id}/{unidade_id} ao processar '{register_name}'")
                            pass # It's okay if not all 'leituras' have this, though CardGraph might expect it.

                        response.append({
                            'title': f'{usina_id} {unidade_id}',
                            'key': register_name, # e.g., "Potência Ativa"
                            'value': register_value,
                            'tipo': 'kVA', # This is often hardcoded or needs to come from config
                            'potencia_maxima': pot_max_val,
                            'tempo': time_taken
                        })
                else:
                     logger_alarms.warning(f"Formato de dados inesperado em enrich_clp_data para {usina_id}/{unidade_id}/{select_type_of_data_fetched}: registers_dict não é um dicionário: {registers_dict}")
        # Boolean alarms ('alarmes' type) are processed directly in fetch_and_process_alarms
        # and don't need to go through this generic 'response' list creation.

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
    # Fetch 'leituras' data (e.g., Potência Ativa)
    logger_alarms.info("get_current_values: Buscando dados de 'leituras'.")
    clp_info_leituras, results_leituras = fetch_all_clp_data('leituras')
    response_leituras = enrich_clp_data(clp_info_leituras, results_leituras, 'leituras')
    potencias = filter_and_sort(response_leituras, 'Potência Ativa')

    # Fetch 'temperaturas' data to populate history and for current values
    logger_alarms.info("get_current_values: Buscando dados de 'temperaturas'.")
    clp_info_temps, results_temps = fetch_all_clp_data('temperaturas') # This call fetches temp data
    # enrich_clp_data (called with 'temperaturas') will populate temperature_history
    _ = enrich_clp_data(clp_info_temps, results_temps, 'temperaturas')

    # The 'temperaturas' list for CardTemperature will now be generated by the new get_temperaturas()
    # which uses the populated temperature_history.
    temperaturas_for_cards, temperature_attention_events = get_temperaturas(None)

    # Aggregate all attention events if needed, or handle them separately
    # For now, just returning temp attention events from this function
    return potencias, temperaturas_for_cards, temperature_attention_events

async def _gather_data(tasks):
    return await asyncio.gather(*tasks) 


def get_temperaturas(select_type): # select_type might be unused now
    """
    Constructs the list of temperature data objects for CardTemperature,
    using the globally stored temperature_history.
    """
    logger_alarms.info("Gerando dados de temperatura para cards a partir do histórico.")
    processed_temperaturas = []
    attention_events_for_temps = [] # List to hold attention events from temperatures
    current_time = time.time()

    for usina_id, usina_data in leituras.items():
        for unidade_id, unidade_data in usina_data.get('CLPS', {}).items():
            temp_points_config = unidade_data.get('temperaturas', {}).get('REAL', {})
            for temp_point_name, config_details in temp_points_config.items():
                history_key = (usina_id, unidade_id, temp_point_name)
                history_deque = temperature_history.get(history_key, deque(maxlen=MAX_HISTORY_POINTS))

                # Format history for the card: dict of {timestamp_str: value}
                # The card might need to be adapted if it expects specific string formats for timestamps.
                # For simplicity, using relative time or simple sequence for now.
                # Let's use relative timestamps for now, or just sequence if card can handle it.
                # For this example, using a simple sequence of last N points.
                # The card component might need updates to render this correctly.

                # card_historico = {str(i): val for i, (_, val) in enumerate(history_deque)}
                # A better history for plotting might be list of [timestamp, value]
                card_historico_list = list(history_deque) # list of (timestamp, value) tuples

                current_temp_value = None
                if history_deque:
                    _, current_temp_value = history_deque[-1] # Get the latest value

                if current_temp_value is None: # Cannot process further without a current value
                    logger_alarms.debug(f"Sem valor atual para {history_key}, pulando análise de eventos de atenção.")
                else:
                    # --- Calculate Rate of Change ---
                    if len(history_deque) >= 2:
                        ts_curr, temp_curr = history_deque[-1]
                        ts_prev, temp_prev = history_deque[-2]

                        delta_temp = temp_curr - temp_prev
                        delta_time_seconds = ts_curr - ts_prev

                        if delta_time_seconds > 0: # Avoid division by zero
                            delta_time_minutes = delta_time_seconds / 60.0
                            rate_of_change_per_minute = delta_temp / delta_time_minutes if delta_time_minutes > 0 else float('inf') * delta_temp

                            if rate_of_change_per_minute >= RATE_OF_CHANGE_THRESHOLD:
                                event_desc = (f"Aumento rápido de temp. em {temp_point_name} ({usina_id}-{unidade_id}): "
                                              f"{rate_of_change_per_minute:.1f}°/min "
                                              f"(de {temp_prev:.1f}° para {temp_curr:.1f}° em {delta_time_seconds:.0f}s)")
                                attention_events_for_temps.append({
                                    'usina_id': usina_id,
                                    'unidade_id': unidade_id,
                                    'descricao': event_desc,
                                    'criticidade': 'Aviso', # Standardized criticality for these events
                                    'tipo_evento': 'taxa_mudanca' # For potential specific handling later
                                })
                                logger_alarms.info(f"EVENTO DE ATENÇÃO (Taxa de Mudança): {event_desc}")

                    # --- Check Proximity to Alarm ---
                    alarm_threshold_value = config_details.get('alarm_threshold_value')
                    if alarm_threshold_value is not None and alarm_threshold_value > 0:
                        # proximity_raw = current_temp_value / alarm_threshold_value
                        # if proximity_raw >= (1.0 - (PROXIMITY_PERCENTAGE_THRESHOLD / 100.0)) and current_temp_value < alarm_threshold_value:
                        # Corrected proximity logic: check if current is >= (threshold - X% of threshold)
                        lower_bound_for_proximity = alarm_threshold_value * (1 - (PROXIMITY_PERCENTAGE_THRESHOLD / 100.0))
                        if lower_bound_for_proximity <= current_temp_value < alarm_threshold_value :
                             event_desc = (f"Temp. em {temp_point_name} ({usina_id}-{unidade_id}) ({current_temp_value:.1f}°) "
                                           f"próxima do alarme ({alarm_threshold_value:.1f}°). "
                                           f"({PROXIMITY_PERCENTAGE_THRESHOLD}% de proximidade)")
                             attention_events_for_temps.append({
                                 'usina_id': usina_id,
                                 'unidade_id': unidade_id,
                                 'descricao': event_desc,
                                 'criticidade': 'Aviso',
                                 'tipo_evento': 'proximidade_alarme'
                             })
                             logger_alarms.info(f"EVENTO DE ATENÇÃO (Proximidade Alarme): {event_desc}")

                # Get alarm/trip thresholds from config_details
                alarm_threshold = config_details.get('alarm_threshold_value', 70.0) # Default if not defined
                trip_threshold = config_details.get('trip_threshold_value', 80.0)  # Default if not defined

                # The 'nome' for CardTemperature should be descriptive
                descriptive_name = f"{usina_id} - {unidade_id} - {temp_point_name}"

                temp_data_for_card = {
                    "nome": descriptive_name,
                    "historico_list": card_historico_list, # Send as list of [ts, val]
                    "atual": current_temp_value,
                    "alarme": alarm_threshold, # Use value from config
                    "trip": trip_threshold,   # Use value from config
                    # We might also need to pass the config for alarm/trip status bit registers
                    # if CardTemperature is to show their status, but it currently expects thresholds.
                    "alarm_status_register_info": config_details.get('alarm_config'),
                    "trip_status_register_info": config_details.get('trip_config')
                }
                processed_temperaturas.append(temp_data_for_card)
                logger_alarms.debug(f"Dados de temperatura processados para card {descriptive_name}: Atual={current_temp_value}, Histórico com {len(card_historico_list)} pontos.")

    if not processed_temperaturas:
        logger_alarms.warning("Nenhum dado de temperatura processado para os cards. Verifique a configuração e o histórico.")
    
    logger_alarms.info(f"Total de {len(attention_events_for_temps)} eventos de atenção de temperatura gerados.")
    return processed_temperaturas, attention_events_for_temps


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

# --- Alarm Processing Functions ---
import logging
logger_alarms = logging.getLogger(__name__ + ".alarms") # Dedicated logger for alarm functions

def get_alarm_definitions(usina_id: str, unidade_id: str) -> dict:
    """
    Extracts all alarm definitions for a given usina and unidade from the
    leituras configuration.

    Returns a dictionary where keys are register addresses (as strings) and
    values are dicts with {'descricao', 'criticidade', 'usina', 'unidade'}.
    """
    alarm_definitions = {}
    logger_alarms.info(f"Buscando definições de alarme para Usina: {usina_id}, Unidade: {unidade_id}")

    try:
        usina_config = leituras.get(usina_id)
        if not usina_config:
            logger_alarms.error(f"Configuração da usina '{usina_id}' não encontrada em get_alarm_definitions.")
            return alarm_definitions

        clp_config = usina_config.get('CLPS', {}).get(unidade_id)
        if not clp_config:
            logger_alarms.error(f"Configuração da unidade CLP '{unidade_id}' na usina '{usina_id}' não encontrada.")
            return alarm_definitions

        # Process boolean alarms
        boolean_alarms = clp_config.get('alarmes', {}).get('BOOLEAN', {})
        for desc, alarm_info in boolean_alarms.items():
            if isinstance(alarm_info, dict) and 'register' in alarm_info and 'criticidade' in alarm_info:
                reg_addr = str(alarm_info['register'])
                alarm_definitions[reg_addr] = {
                    'descricao': desc, # This 'desc' is the original key from config
                    'criticidade': alarm_info['criticidade'],
                    'usina': usina_id,
                    'unidade': unidade_id,
                    'tipo': 'BOOLEAN',
                    'original_config_key': desc # Store the original key for boolean alarms too
                }
            else:
                logger_alarms.warning(f"Formato inesperado para alarme booleano '{desc}' em {usina_id}/{unidade_id}: {alarm_info}")


        # Process temperature alarms
        temp_configs = clp_config.get('temperaturas', {}).get('REAL', {})
        for temp_point_name, temp_data in temp_configs.items():
            if isinstance(temp_data, dict):
                # Alarm level for temperature
                alarm_conf = temp_data.get('alarm_config')
                if alarm_conf and isinstance(alarm_conf, dict) and 'register' in alarm_conf and 'criticidade' in alarm_conf:
                    reg_addr_alarm = str(alarm_conf['register'])
                    # Find the original key for this alarm_config register
                    # This assumes alarm_config's register is unique enough to find its key.
                    # A better way would be to pass the original key if the structure allowed.
                    # For now, we assume the 'descricao' for these will be synthetic.
                    # The 'original_config_key' should be the key that get_data will return for this status bit.
                    # This requires knowing how 'alarm_config' and 'trip_config' are named if they are read as separate items by get_data.
                    # Based on current get_data, it reads what's in 'config.py'.
                    # The 'alarm_config' and 'trip_config' are dicts, not direct registers for get_data's "registers" param.
                    # This means the current get_data for 'temperaturas' only reads the 'value' registers.
                    # THIS IS A SIGNIFICANT GAP.
                    # For now, let's assume 'alarm_config' and 'trip_config' contain the *names* of separate boolean registers
                    # that would be read if 'temperaturas' also had a 'BOOLEAN' section.
                    #
                    # Re-evaluating the structure of config and get_data for temperature alarms:
                    # The config has: "Enrolamento Fase A": { 'value': REG_VAL, 'alarm_config': {'register': REG_ALARM_BIT, ...}, ... }
                    # get_data called with type 'temperaturas' would target leituras[usina]['CLPS'][unidade]['temperaturas'].
                    # The current get_data would only process the 'REAL' part: {'Enrolamento Fase A': REG_VAL}.
                    # It does NOT automatically pick up REG_ALARM_BIT.
                    #
                    # To make this work as per subtask description (reading status bits):
                    # 1. REG_ALARM_BIT and REG_TRIP_BIT must be part of a BOOLEAN group within 'temperaturas',
                    #    OR 'alarmes' section should also contain these bits.
                    # 2. OR, get_data needs to be much more sophisticated.
                    #
                    # Given the simplification "Chamar get_data para config_type = 'alarmes' ... e para 'temperaturas'",
                    # we must assume these alarm bits are defined under 'alarmes' or a similar BOOLEAN section.
                    # The current get_alarm_definitions correctly extracts them if they are in 'alarmes'.
                    # If 'alarm_config':{'register':...} is meant to be a status bit read via the 'alarmes' group:
                    # We need to ensure these registers are also listed in the 'alarmes':'BOOLEAN' section of config.py.
                    # The subtask implies they are status bits.
                    #
                    # Let's assume the 'register' in 'alarm_config' and 'trip_config' *are* separate boolean status registers
                    # and that they are defined somewhere that `get_data(..., tipo='alarmes')` would read them.
                    # The `get_alarm_definitions` correctly creates entries for them, keyed by their register address.
                    # The `descricao` is synthetic e.g. "Temperatura Enrolamento Fase A - Alarme".
                    # The `original_config_key` for these will be this synthetic `descricao` if we want to look them up
                    # in a hypothetical combined data structure. But it's better to use their actual key from config if possible.

                    # For now, let's stick to the assumption that these are boolean status bits.
                    # Their 'original_config_key' will be the synthetic description, as that's what we have.
                    # This means `get_data` for 'alarmes' must return these synthetic descriptions as keys if it were to read them.
                    # This points to a mismatch in how `get_data` returns keys vs. how `get_alarm_definitions` generates them for temps.

                    # Correct approach: The 'alarm_config' and 'trip_config' registers are boolean status registers.
                    # `get_alarm_definitions` will create entries for them.
                    # When we call `get_data` for 'alarmes', its response `data['BOOLEAN']` will be keyed by
                    # the *original descriptions* from `config.py`'s `alarmes.BOOLEAN` section.
                    # So, for these temperature status bits to be read, their *original descriptive key from config.py*
                    # and their register address must be consistent.
                    # `get_alarm_definitions` should store the *actual key from config.py* if these temp alarm bits
                    # are duplicated in the main "alarmes" section.
                    # This is getting too complex for one step. Let's follow the subtask's direct implication:
                    # "alarm_config" and "trip_config" registers ARE status bits.
                    # We will assume they are read when we ask for 'alarmes'.
                    # `get_alarm_definitions` creates entries for them. The `descricao` is synthetic.
                    # We need to map this synthetic `descricao` back to the key `get_data` would use.
                    # This implies `get_data` would need to be aware of these synthetic descriptions.
                    #
                    # Simplest path: Assume `alarm_config` and `trip_config` registers are read along with other booleans
                    # when `get_data` is called for the main "alarmes" type. And that `get_data` result keys match
                    # the descriptions in `config.py`.
                    # The `get_alarm_definitions` for temp alarms creates synthetic descriptions.
                    # These synthetic descriptions won't match keys from `get_data(..., tipo='alarmes')`.

                    # Sticking to the provided structure of get_alarm_definitions:
                    # It produces definitions where key is reg_addr. 'descricao' is synthetic for temp alarms.
                    # We need to find the value for reg_addr from the `get_data` output.
                    # The `get_data` output is keyed by original config descriptions.
                    # So, we need a reverse mapping: reg_addr -> original_config_description.
                    # This reverse mapping can be built by iterating config once.

                    # For this step, I will modify get_alarm_definitions to store the original config key
                    # if the alarm is a temperature status bit that is ALSO defined in the main 'alarmes' section.
                    # This is the only way to reconcile the current structures.
                    # However, the problem states "alarm_config... are bits of status". It does not state they are duplicated.

                    # Let's assume the structure of `config.py` implies that `alarm_config` and `trip_config`
                    # are *not* fetched via the 'alarmes' general call, but would be part of 'temperaturas' if it read booleans.
                    # Since `get_data` for 'temperaturas' only reads 'REAL', these status bits are not read by current `get_data`.
                    # This is a problem for the "Suposição para esta tarefa" (that they are status bits).

                    # Given the constraint: "Simplificação para esta sub-tarefa: ... Chamar get_data para config_type = 'alarmes' ... e para 'temperaturas'"
                    # This means any REAL_ALARM/TRIP status bits *must* be readable via one of these calls.
                    # If they are boolean status bits, they'd be read by `tipo='alarmes'`.
                    # If their values are compared to thresholds, the *temperature value* is read by `tipo='temperaturas'`.

                    # The subtask's assumption: "os registradores em alarm_config e trip_config são bits de status".
                    # This means they are boolean. They should be read by `get_data` when `config_type='alarmes'`.
                    # `get_alarm_definitions` creates entries for them, keyed by `reg_addr_alarm` and `reg_addr_trip`.
                    # The `descricao` is synthetic: "Temperatura {temp_point_name} - Alarme/Trip".
                    # To find their value, we need to look up `reg_addr_alarm` in the output of `get_data(...,config_type='alarmes')`.
                    # The output of `get_data(...,config_type='alarmes')` is `{'BOOLEAN': {ORIGINAL_DESC_FROM_CONFIG: value}}`.
                    # So, we need a map from `reg_addr_alarm` to `ORIGINAL_DESC_FROM_CONFIG`.
                    # This map can be built by pre-scanning `leituras[usina_id]['CLPS'][unidade_id]['alarmes']['BOOLEAN']`.

                    # Let's make get_alarm_definitions store this `original_config_key` for ALL alarms.

                    alarm_definitions[reg_addr_alarm] = {
                        'descricao': f"Temperatura {temp_point_name} - Alarme", # Synthetic description for this specific combined alarm condition
                        'criticidade': alarm_conf['criticidade'],
                        'usina': usina_id,
                        'unidade': unidade_id,
                        'tipo': 'REAL_ALARM',
                        'value_register': temp_data.get('value'), # Address of the actual temperature REAL value
                        'status_register': alarm_conf['register'], # Address of the BOOLEAN status bit
                        'original_config_key_status_bit': "" # Will be populated if this status bit is found in main 'alarmes' section
                    }
                else:
                    logger_alarms.warning(f"Configuração de alarme de temperatura ('alarm_config') incompleta ou malformada para '{temp_point_name}' em {usina_id}/{unidade_id}: {alarm_conf}")

                trip_conf = temp_data.get('trip_config')
                if trip_conf and isinstance(trip_conf, dict) and 'register' in trip_conf and 'criticidade' in trip_conf:
                    reg_addr_trip = str(trip_conf['register'])
                    alarm_definitions[reg_addr_trip] = {
                        'descricao': f"Temperatura {temp_point_name} - Trip",
                        'criticidade': trip_conf['criticidade'],
                        'usina': usina_id,
                        'unidade': unidade_id,
                        'tipo': 'REAL_TRIP',
                        'value_register': temp_data.get('value'),
                        'status_register': trip_conf['register'],
                        'original_config_key_status_bit': "" # Will be populated
                    }
                else:
                    logger_alarms.warning(f"Configuração de trip de temperatura ('trip_config') incompleta ou malformada para '{temp_point_name}' em {usina_id}/{unidade_id}: {trip_conf}")
            else:
                logger_alarms.warning(f"Formato inesperado para configuração de temperatura '{temp_point_name}' em {usina_id}/{unidade_id}: {temp_data}")


    except Exception as e:
        logger_alarms.error(f"Erro ao processar definições de alarme para {usina_id}/{unidade_id}: {e}", exc_info=True)


    # Post-process to find original_config_key for temperature status bits if they are defined in main 'alarmes'
    main_boolean_alarms_by_reg = {str(bv['register']): bk for bk, bv in clp_config.get('alarmes', {}).get('BOOLEAN', {}).items() if isinstance(bv, dict)}
    for reg_addr_key, alarm_def_item in alarm_definitions.items():
        if alarm_def_item['tipo'] in ['REAL_ALARM', 'REAL_TRIP']:
            status_reg_addr = str(alarm_def_item.get('status_register'))
            if status_reg_addr in main_boolean_alarms_by_reg:
                alarm_def_item['original_config_key_status_bit'] = main_boolean_alarms_by_reg[status_reg_addr]
            else:
                # This status bit is not in the main 'alarmes' list, so it cannot be read by get_data(..., tipo='alarmes')
                # unless get_data is modified or these definitions are added to config.py's main 'alarmes'
                logger_alarms.warning(f"Status bit register {status_reg_addr} for temperature alarm '{alarm_def_item['descricao']}' "
                                      f"em {usina_id}/{unidade_id} não encontrado na seção principal 'alarmes'. Não será possível ler seu estado com a chamada genérica de 'alarmes'.")


    logger_alarms.info(f"Definições de alarme encontradas para {usina_id}/{unidade_id}: {len(alarm_definitions)} itens.")
    logger_alarms.debug(f"Definições detalhadas para {usina_id}/{unidade_id}: {alarm_definitions}")
    return alarm_definitions


async def fetch_and_process_alarms() -> list:
    """
    Fetches current alarm statuses by reading relevant registers and
    comparing them against their definitions.
    """
    logger_alarms.info("Iniciando fetch_and_process_alarms...")
    active_alarms_list = []

    # Example usinas/unidades to process for now

    # Iterate over all usinas and unidades defined in leituras
    # For now, using the example_units for focused testing as per previous steps
    example_units = [
        ("CGH FAE", "UG-01"),
        ("CGH APARECIDA", "UG-01")
    ]
    # To process all:
    # all_units = []
    # for usina_id_cfg, usina_data_cfg in leituras.items():
    #     for unidade_id_cfg in usina_data_cfg.get('CLPS', {}).keys():
    #         all_units.append((usina_id_cfg, unidade_id_cfg))

    for usina_id, unidade_id in example_units: # Replace with all_units to process everything
        logger_alarms.info(f"Processando alarmes para Usina: {usina_id}, Unidade: {unidade_id}")

        alarm_definitions = get_alarm_definitions(usina_id, unidade_id)
        if not alarm_definitions:
            logger_alarms.warning(f"Nenhuma definição de alarme encontrada para {usina_id}/{unidade_id}. Pulando.")
            continue

        logger_alarms.info(f"Total de {len(alarm_definitions)} definições de alarme para {usina_id}/{unidade_id}.")

        clp_boolean_data_values = {}
        # clp_temperature_values = {} # For actual temperature REAL values, not used in this simplified version

        # --- Fetch Boolean Alarm Data ---
        # According to simplification, call get_data for 'alarmes' type.
        # This should fetch all registers defined under leituras[usina_id]['CLPS'][unidade_id]['alarmes']['BOOLEAN']

        clp_unit_config = leituras[usina_id].get('CLPS', {}).get(unidade_id, {})
        conexao_info = clp_unit_config.get('conexao')

        if not conexao_info:
            logger_alarms.error(f"Informação de conexão não encontrada para {usina_id}/{unidade_id}. Não é possível buscar dados de alarme.")
            continue

        # Check if there are any boolean type alarms defined (directly or as status bits for temps)
        # This determines if we need to call get_data for the 'alarmes' category.
        # The 'alarmes' key in config.py is assumed to be the one containing BOOLEAN alarm definitions.
        boolean_alarm_definitions_in_config = clp_unit_config.get('alarmes', {}).get('BOOLEAN', {})

        if boolean_alarm_definitions_in_config:
            logger_alarms.info(f"Buscando dados de alarmes booleanos para {usina_id}/{unidade_id}.")
            service_config_alarms = {
                'ip': leituras[usina_id]['ip'],
                'port': leituras[usina_id]['port'],
                'tipo': 'alarmes' # This 'tipo' is the main key in config for this group of registers
            }
            # Construct the 'data' payload for get_data
            # get_data expects data[config['tipo']] to contain the register definitions
            # So, data_payload_alarms should be {'conexao': ..., 'alarmes': {'BOOLEAN': {desc1: addr1, ...}}}
            data_payload_alarms = {
                'conexao': conexao_info,
                'alarmes': {'BOOLEAN': boolean_alarm_definitions_in_config} # Pass the actual definitions
            }

            try:
                # get_data returns: result_dict, time_taken
                # result_dict is like: {'BOOLEAN': {'[01.00]...': True, ...}}
                fetched_boolean_data, _ = await get_data(service_config_alarms, data_payload_alarms)
                if fetched_boolean_data and 'BOOLEAN' in fetched_boolean_data:
                    clp_boolean_data_values = fetched_boolean_data['BOOLEAN']
                    logger_alarms.info(f"Dados de alarmes booleanos recebidos para {usina_id}/{unidade_id}: {clp_boolean_data_values}")
                else:
                    logger_alarms.warning(f"Nenhum dado BOOLEAN retornado por get_data para 'alarmes' em {usina_id}/{unidade_id}. Resposta: {fetched_boolean_data}")
            except Exception as e:
                logger_alarms.error(f"Erro ao buscar dados de alarmes booleanos para {usina_id}/{unidade_id}: {e}", exc_info=True)
                continue # Skip processing for this unit if data fetch fails
        else:
            logger_alarms.info(f"Nenhuma definição de alarme BOOLEAN na configuração principal de 'alarmes' para {usina_id}/{unidade_id}. Não é necessário buscar.")


        # --- Process Alarms ---
        for reg_addr_str, alarm_def in alarm_definitions.items():
            alarm_is_active = False
            descriptive_key_for_lookup = alarm_def.get('original_config_key') # For BOOLEAN alarms from main 'alarmes'

            if alarm_def['tipo'] == 'BOOLEAN':
                if not descriptive_key_for_lookup: # Should always be there now
                     logger_alarms.warning(f"Alarme BOOLEAN {alarm_def['descricao']} não possui 'original_config_key'. Não é possível verificar estado.")
                     continue
                value = clp_boolean_data_values.get(descriptive_key_for_lookup)
                logger_alarms.debug(f"Verificando Alarme BOOLEAN: Usina={usina_id}, Unidade={unidade_id}, Desc='{alarm_def['descricao']}' (Chave Original='{descriptive_key_for_lookup}'), RegEnd={reg_addr_str}, ValorLido={value}")
                if value is True:
                    alarm_is_active = True

            elif alarm_def['tipo'] in ['REAL_ALARM', 'REAL_TRIP']:
                # These are status bits from temperature sensors, assumed to be part of the main 'alarmes' boolean block.
                status_bit_original_key = alarm_def.get('original_config_key_status_bit')
                if not status_bit_original_key:
                    logger_alarms.warning(f"Alarme de Temperatura (Status Bit) {alarm_def['descricao']} não possui 'original_config_key_status_bit' ou não foi encontrado na seção 'alarmes'. Não é possível verificar estado. RegEnd={alarm_def.get('status_register')}")
                    continue

                value = clp_boolean_data_values.get(status_bit_original_key)
                logger_alarms.debug(f"Verificando Alarme Temperatura (Status Bit): Usina={usina_id}, Unidade={unidade_id}, Desc='{alarm_def['descricao']}' (Chave Original Status Bit='{status_bit_original_key}'), RegEnd Status Bit={alarm_def.get('status_register')}, ValorLido={value}")
                if value is True:
                    alarm_is_active = True

            if alarm_is_active:
                active_alarm_info = {
                    'usina_id': alarm_def['usina'],
                    'unidade_id': alarm_def['unidade'],
                    'descricao': alarm_def['descricao'], # Use the synthetic/main description
                    'criticidade': alarm_def['criticidade']
                }
                active_alarms_list.append(active_alarm_info)
                logger_alarms.warning(f"ALARME ATIVO DETECTADO: {active_alarm_info}") # Log as warning for visibility

    logger_alarms.info(f"fetch_and_process_alarms concluído. Total de alarmes ativos encontrados: {len(active_alarms_list)}")
    logger_alarms.debug(f"Lista de alarmes ativos: {active_alarms_list}")
    return active_alarms_list

# Example of how to run the async function if needed directly (for testing)
# if __name__ == '__main__':
#     asyncio.run(fetch_and_process_alarms())
