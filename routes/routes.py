import logging # Added import
import logging
import asyncio # Added import
from flask import render_template, jsonify, Response, request
from models.config import leituras
from main import app
from models.load_data import get_data, get_current_values, get_usinas, get_temperaturas, fetch_and_process_alarms # Added import
from models.control_commands import send_command
from components.potencia_ativa import CardGraph
from components.temperaturas import CardTemperature
from components.alarm_panel import AlarmPanel # Added import
from models.reset_alarmes import reset_alarmes
import time
import json
tempo_total = 0
contador = 0
conta = 0

@app.route("/")
def index():
    """
    Rota principal da aplicação.
    
    Esta rota é responsável por renderizar a página inicial, exibindo os cards de Potência Ativa e Temperatura.
    Não recebe argumentos externos (query params, body, etc). Todos os dados são buscados internamente.
    
    Returns:
        Response: Página HTML renderizada com os componentes de Potência Ativa e Temperatura.
    """
    select_type = 'leituras'
    inicio = time.time()
    name_potencia = 'Potência Ativa'
    name_temperatura = 'Temperatura'
    # get_current_values now returns: potencias, temperaturas_for_cards, temperature_attention_events
    potencias, temperaturas_for_cards, temp_attention_events = asyncio.run(get_current_values(select_type))
    # temperaturas variable is no longer separately assigned here as get_temperaturas is part of get_current_values
    
    # lines_potencia = get_data(name_potencia, select_type)
    # lines_temperatura = get_data(name_temperatura, select_type)
    fim = time.time() - inicio

    html_potencia_ativa = _render_card_graph(name_potencia, fim, potencias)
    # Corrected: Use temperaturas_for_cards for rendering the temperature component
    html_temperature = _render_card_temperature(name_temperatura, fim, temperaturas_for_cards)

    # Fetch regular alarms and combine with temperature attention events
    logger_index = logging.getLogger(__name__ + ".index")
    logger_index.info("Fetching regular alarms for initial page load.")
    active_regular_alarms = asyncio.run(fetch_and_process_alarms())
    logger_index.info(f"Found {len(active_regular_alarms)} regular active alarms.")
    logger_index.info(f"Found {len(temp_attention_events)} temperature attention events.")

    combined_alerts = active_regular_alarms + temp_attention_events
    logger_index.info(f"Total combined alerts for panel: {len(combined_alerts)}")

    alarm_panel_component = AlarmPanel(combined_alerts)
    html_alarm_panel = alarm_panel_component.html()

    return render_template(
        "index.html",
        html_potencia_ativa=html_potencia_ativa,
        html_temperature=html_temperature, # This should use temperaturas_for_cards
        html_alarm_panel=html_alarm_panel
    )

def _render_card_graph(name, tempo, lines):
    """Gera o HTML do card de Potência Ativa."""
    card = CardGraph(name, tempo, lines)
    return card.html()

def _render_card_temperature(name, tempo, lines):
    """Gera o HTML do card de Temperatura."""
    card_temperature = CardTemperature(name, tempo, lines)
    return card_temperature.html()

# def get_data(name, select_type):
#     """
#     Filtra e ordena os dados retornados por get_current_values, buscando apenas os itens cujo 'key' corresponde ao nome informado.
#     Os resultados são ordenados de forma decrescente pelo valor, colocando valores None por último.

#     Args:
#         name (str): Nome da chave a ser filtrada.
#         select_type (str): Tipo de seleção para buscar os dados.

#     Returns:
#         list: Lista de dicionários filtrados e ordenados.
#     """
#     data = get_current_values(select_type)
#     filtered_lines = [line for line in data if line['key'] == name]
#     sorted_lines = sorted(
#         filtered_lines,
#         key=lambda x: (x['value'] is None, x['value'] if x['value'] is not None else float('-inf')),
#         reverse=True
#     )
#     return sorted_lines

@app.route('/stream')
def stream():
    def gerar_eventos():
        select_type = 'leituras'
        while True:
            inicio = time.time()
            # lines = get_data('Potência Ativa', select_type)
            name_potencia = 'Potência Ativa'
            name_temperatura = 'Temperatura' # Title for the card section

            # Get all data including temperature attention events
            potencias_sse, temperaturas_for_cards_sse, temp_attention_events_sse = asyncio.run(get_current_values(select_type))
            # temperaturas_sse = get_temperaturas(select_type) # Called within get_current_values

            fim = time.time() - inicio
            
            card_potencia_sse = CardGraph(name_potencia, fim, potencias_sse)
            card_temperatura_sse = CardTemperature(name_temperatura, fim, temperaturas_for_cards_sse)

            # Fetch regular alarms and combine with temperature attention events for SSE
            logger_sse = logging.getLogger(__name__ + ".sse")
            logger_sse.debug("Fetching regular alarms for SSE update.")
            active_regular_alarms_sse = asyncio.run(fetch_and_process_alarms())
            logger_sse.debug(f"Found {len(active_regular_alarms_sse)} regular active alarms for SSE.")
            logger_sse.debug(f"Found {len(temp_attention_events_sse)} temperature attention events for SSE.")

            combined_alerts_sse = active_regular_alarms_sse + temp_attention_events_sse
            logger_sse.debug(f"Total combined alerts for SSE panel: {len(combined_alerts_sse)}")

            alarm_panel_component_sse = AlarmPanel(combined_alerts_sse)
            html_alarm_panel_sse = alarm_panel_component_sse.html()

            data = {
                'html_potencia_ativa': card_potencia_sse.html(),
                'html_temperature': card_temperatura_sse.html(),
                'html_alarm_panel': html_alarm_panel_sse
            }
            # Envia os dados no formato JSON
            yield f'data: {json.dumps(data)}\n\n'
            time.sleep(20) # Consider making this configurable or dynamic based on load
    return Response(gerar_eventos(), mimetype='text/event-stream')

@app.route('/api/command/<usina_id>/<unidade_id>/<comando>', methods=['POST'])
def handle_command(usina_id: str, unidade_id: str, comando: str):
    """
    Receives control commands and sends them to the placeholder function.
    """
    logger = logging.getLogger(__name__) # Get logger instance

    # Log incoming request
    request_payload = request.json if request.is_json else None
    logger.info(
        f"Rota de comando acessada: {request.method} {request.path} por IP {request.remote_addr}. "
        f"Path Params: usina_id='{usina_id}', unidade_id='{unidade_id}', comando='{comando}'. "
        f"JSON Payload: {request_payload}"
    )

    data = request.get_json(silent=True)
    valor = data.get('valor') if data else None

    success, message = send_command(usina_id, unidade_id, comando, valor)

    response_json = {'status': 'success' if success else 'error', 'message': message}
    response_status_code = 200 if success else 400 # Use 400 for client-side type errors, 500 for true server errors

    # Log outgoing response
    logger.info(
        f"Resposta da rota de comando {request.path}: Status={response_status_code}, JSON={response_json}"
    )

    if success:
        return jsonify(response_json), response_status_code
    else:
        return jsonify(response_json), response_status_code

