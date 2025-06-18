class CardGraph:
    '''Card component - para mostrar as informações sobre a usina hidroelétrica'''

    def __init__(self, title, tempo, lines):
        self.title = title
        self.tempo = tempo
        self.lines = lines

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
        for line in self.lines:
            valor = line.get('value')
            try:
                valor_float = float(valor)
                msg = f'{int(valor_float)} {line.get("tipo", "kVA")}'
                value_max = line.get('potencia_maxima')
                width = (valor_float / value_max * 100) if value_max > 0 else 0
                color = 'var(--green-a)'
            except (TypeError, ValueError):
                msg = 'Desconectado'
                width = 0
                color = 'var(--red)'

            # Extrair usina_id e unidade_id do título
            title_parts = line['title'].split(" - ")
            usina_id = title_parts[0] if len(title_parts) > 0 else "DESCONHECIDA"
            unidade_id = title_parts[1] if len(title_parts) > 1 else "DESCONHECIDA"

            html += f"""
                <div class="line-item">
                    <div class="line-info">
                        <div class="line-title">
                            <p class="line-title-text">{line['title']}</p>
                        </div>
                        <div class="line-value">
                            <div class="line-value-bar" style="width: {width}%"></div>
                            <span class="line-title-value" style="background-color: {color};">{msg}</span>
                            <span class="line-title-value-max">{line['potencia_maxima']} {line.get("tipo", "kVA")}</span>
                        </div>
                    </div>
                    <div class="line-controls">
                        <button class="btn-command" data-usina-id="{usina_id}" data-unidade-id="{unidade_id}" data-comando="LIGAR">Ligar</button>
                        <button class="btn-command" data-usina-id="{usina_id}" data-unidade-id="{unidade_id}" data-comando="DESLIGAR">Desligar</button>
                        <div class="control-group">
                            <input type="number" class="input-potencia" placeholder="Potência (%)" id="potencia-{usina_id}-{unidade_id}">
                            <button class="btn-command btn-ajustar" data-usina-id="{usina_id}" data-unidade-id="{unidade_id}" data-comando="AJUSTAR_POTENCIA" data-input-id="potencia-{usina_id}-{unidade_id}">Enviar</button>
                        </div>
                    </div>
                </div>
                """
        html += "</div>"
        html += "</div>"
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
        raw_html = self.render()
        # Minify HTML by removing unnecessary whitespace
        html = ' '.join(raw_html.split())
        return html
