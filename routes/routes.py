from flask import render_template, jsonify, Response, request
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
usina = 0

@app.route("/")
def index():
    """
    Rota principal da aplicação.
    
    Esta rota é responsável por renderizar a página inicial, exibindo os cards de Potência Ativa e Temperatura.
    Não recebe argumentos externos (query params, body, etc). Todos os dados são buscados internamente.
    
    Returns:
        Response: Página HTML renderizada com os componentes de Potência Ativa e Temperatura.
    """
    global usina
    # usina = 'Todas'
    
    select_type = 'leituras'
    inicio = time.time()
    name_potencia = 'Potência Ativa'
    name_temperatura = 'Temperatura'
    potencias= get_current_values(select_type)
    print('Executando get_temperaturas')
    temperaturas = get_temperaturas()
    
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
    global usina
    card = CardGraph(name, tempo, lines, usina)
    return card.html()

def _render_card_temperature(name, tempo, lines):
    """Gera o HTML do card de Temperatura."""
    global usina
    card_temperature = CardTemperature(name, tempo, lines, usina)
    return card_temperature.html()

@app.route('/stream')
def stream():
    def gerar_eventos():
        select_type = 'leituras'
        while True:
            inicio = time.time()
            # lines = get_data('Potência Ativa', select_type)
            name_potencia = 'Potência Ativa'
            name_temperatura = 'Temperaturas'
            potencias = get_current_values(select_type)
            temperaturas = get_temperaturas()
            # lines_temperature = get_data('Temperaturas', select_type)

            fim = time.time() - inicio
            
            # Criar o card e renderizar o HTML
            card = CardGraph(name_potencia, fim, potencias, usina)
            card_temperature = CardTemperature(name_temperatura, fim, temperaturas, usina)
            data = {
                'html_potencia_ativa': card.html(),
                'html_temperature': card_temperature.html(),
                'html': card.html() + card_temperature.html(),
            }
            # Envia os dados no formato JSON
            print('########################')
            print(' ')
            yield f'data: {json.dumps(data)}\n\n'
            time.sleep(8)
    return Response(gerar_eventos(), mimetype='text/event-stream')

@app.route('/usina', methods=['POST'])
def usinas():
    global usina
    usina = request.json['usina']
    print('usina: ', usina)
    return jsonify({'message': 'Usina recebida com sucesso'})


