from datetime import datetime
memoria = 0
class CardGraph:
    '''Card component - para mostrar as informações sobre a usina hidroelétrica'''

    def __init__(self, title, tempo, lines, usina):
        self.title = title
        self.tempo = tempo
        self.lines = lines
        # print('usina: ', usina)
        self.usina = ['Todas', 'Pedras', 'Aparecida', 'FAE', 'Picadas', 'Hoppen'][int(usina)]
        self.memoria = memoria

    def render(self):
        value_max = self.get_value_max() * 1.4
        html =f"""
        <div class="card-graph-content">
            <div class="card-graph-title">
                <div class="card-graph-title-text">{self.title}</div>
                <select class="btn-select">
                    <option value="1">tempo real</option>
                    <option value="2">últimas 24 horas</option>
                    <option value="3">últimos 7 dias</option>
                </select>
            </div>
            <div class="card-graph-body">
                <div class="line">"""
        somatoria = 0
        for line in self.lines:
            # print('line: ', line)
            # print('usina: ', self.usina)
            if self.usina.upper() != 'TODAS' and self.usina.upper() not in line['title'].upper():
                # print('                     usina: ', self.usina, 'not in line: ', line['title'])
                # print('--------------------------------')
                continue
            valor = line.get('value')
            try:
                valor_float = float(valor)
                somatoria += valor_float
                msg = f'{int(valor_float)} {line.get("tipo", "kW")}'
                value_max = line.get('potencia_maxima')
                width = (valor_float / value_max * 100) if value_max > 0 else 0
                color = 'var(--green-a)'
            except (TypeError, ValueError):
                msg = 'Desconectado'
                width = 0
                color = 'var(--red)'
  
            html += f"""
                <div class="line-title">
                    <p class="line-title-text">{line['title']}</p>
                </div>
                <div class="line-value">
                    <div class="line-value-bar" style="width: {width}%"></div>
                    <span class="line-title-value" style="background-color: {color};">{msg}</span>
                    <span class="line-title-value-max">{line['potencia_maxima']} {line.get("tipo", "kW")}</span>
                </div>
                """
        html += "</div>"
        html += "</div>"

        # valor_total = f"R$ {valor_:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        html += f"<div class='card-graph-footer' style='color: var(--black-1); font-weight: bold; font-size: 1.2rem;'>Somatória de potência: {somatoria} kW</div>"
        somatoria_valor = somatoria  * 24 * 0.45
        valor_total = f"R$ {somatoria_valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        # html += f"<div class='card-graph-footer' style='color: var(--black-1); font-weight: bold; font-size: 1.2rem;'>Valor total: {valor_total}</div>"
        html += f"<div class='card-graph-footer' style='color: var(--black-1); font-weight: bold; font-size: 1.2rem;'>Atualizado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</div>"
        html += f"<div class='card-graph-footer'>Tempo de execução: {round(self.tempo, 2)} segundos</div>"
        html += "</div>"
        return html

    def get_value_max(self):
        # Pega apenas valores que podem ser convertidos para float (leituras bem sucedidas)
        valores = []
        for line in self.lines:
            v = line.get('potencia_maxima')
            try:
                if v is not None:
                    valores.append(float(v))
            except (TypeError, ValueError):
                continue
        return max(valores) if valores else 1
    
    def html(self):
        # retirar o espaço em branco do html e caracteres que não são permitidos no html
        html = ''
        for line in self.render().split('\n'):
            html += line.strip()
        return html
