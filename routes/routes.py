from flask import render_template, jsonify, Response
from models.config import leituras
from main import app
from models.load_data import get_data, get_current_values, get_usinas, get_temperaturas
from components.potencia_ativa import CardGraph
from components.temperaturas import CardTemperature
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
    potencias, temperaturas = get_current_values(select_type)
    temperaturas = get_temperaturas(select_type)
    
    # lines_potencia = get_data(name_potencia, select_type)
    # lines_temperatura = get_data(name_temperatura, select_type)
    fim = time.time() - inicio

    html_potencia_ativa = _render_card_graph(name_potencia, fim, potencias)
    html_temperature = _render_card_temperature(name_temperatura, fim, temperaturas)

    return render_template(
        "index.html",
        html_potencia_ativa=html_potencia_ativa,
        html_temperature=html_temperature
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
            name_temperatura = 'Temperaturas'
            potencias, temperaturas = get_current_values(select_type)
            temperaturas = get_temperaturas(select_type)
            # lines_temperature = get_data('Temperaturas', select_type)

            fim = time.time() - inicio
            
            # Criar o card e renderizar o HTML
            card = CardGraph(name_potencia, fim, potencias)
            card_temperature = CardTemperature(name_temperatura, fim, temperaturas)
            data = {
                'html_potencia_ativa': card.html(),
                'html_temperature': card_temperature.html(),
                # 'html': card.html() + card_temperature.html(),
            }
            # Envia os dados no formato JSON
            yield f'data: {json.dumps(data)}\n\n'
            time.sleep(20)
    return Response(gerar_eventos(), mimetype='text/event-stream')


