class CardTemperature:
    def __init__(self, title, tempo, lines, usina):
        self.title = title
        self.tempo = tempo
        self.lines = lines
        self.usina = ['Todas', 'Pedras', 'Aparecida', 'FAE', 'Picadas', 'Hoppen'][int(usina)]
        # self.usinas = {'PEDRAS':'#3AB9A0', 'APARECIDA':'#2B8876', 'FAE':'#2089CA', 'PICADAS':'#7F63FB','HOPPEN':'#D4E023'} 
        self.usinas = {
            # tons "pastel" – continuam distintos, mas sem brigar com o texto preto
            'PEDRAS'   : ['#BFD9D5', '#3AB9A0'],   # teal sutil, verde mais escuro
            'APARECIDA': ['#C5D2C5', '#2B8876'],   # verde musgo claro, verde mais escuro
            'FAE'      : ['#C5CFDF', '#2089CA'],   # azul acinzentado, azul mais escuro
            'PICADAS'  : ['#D4CDE0', '#7F63FB'],   # lilás fumaça, lilás mais escuro
            'HOPPEN'   : ['#E5E1C5', '#D4E023'],   # cáqui pálido, amarelo mais escuro
        }

    def render(self):
        html = f"""
        <div class="card-temperature-content">
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
        usina = ''
        for line in self.lines:
            usina = [ us for us in self.usinas.keys() if us in line['nome']][0]
            color = self.usinas[usina]
            # print('color: ', color, 'usina: ', usina)
            if self.usina.upper() != 'TODAS' and self.usina.upper() not in line['nome'].upper():
                continue
            html += f"""
                <div class="container-temperatura">
                    <div class="describe" >
                        <div class="mancal-guia" style="background-color: {color[0]}; border-left: 8px solid {color[1]};">{line['nome']}</div>
                    </div>
                    <div class="bar">
                        <div class="bar-temp">"""
            
            
            
            for historico in line['historico'].items():
                # Proteção contra divisão por zero
                # Exemplo: trip = 100, alarme = 90, valor atual = 80
                # percent = (valor_atual - alarme) / (trip - alarme) * 100
                if line['trip'] != line['alarme']:
                    percent = min(max((historico[1] - line['alarme']) / (line['trip'] - line['alarme']) * 100, 0), 100)
                else:
                    percent = 0
                # if line['trip']:
                #     percent = min(historico[1] / line['trip'] * 100, 100)   # 0-100 %
                # else:
                #     print('trip: ', line['trip'], 'historico: ', historico[0])
                #     # raise Exception('trip: ', line['trip'], 'historico: ', historico[0], 'usina: ', usina)
                #     percent = 0
                html += f"""
                    <div class="bars" style="--pct:{percent}%; ">
                        <div class="rectangle"></div>
                        <div class="ellipse"></div>
                        <div class="time-label">{historico[0]}</div>
                    </div>"""
                
            col = '#A9E5A9'           # default (baixo risco)
            if   line['risco'] >= 90: col = '#FF7A7A'  # alto
            elif line['risco'] >= 70: col = '#FFD85A'  # médio

            html += f"""
                        </div>
                        <div class="temperaturas">
                            <div class="temperatura-box">
                                <span style="color: #000; font-size: 10px;">atual: </span>
                                <div class="atual"> 
                                    <div class="text-value">{line['atual']} °C</div>
                                </div>
                            </div>
                            <div class="temperatura-box">
                                <span style="color: #000; font-size: 10px;">alarme: </span>
                                <div class="alarme">
                                    <div class="text-value">{line['alarme']} °C</div>
                                </div>
                            </div>
                            <div class="temperatura-box">
                                <span style="color: #000; font-size: 10px;">trip: </span>
                                <div class="trip">
                                    <div class="text-value">{line['trip']} °C</div>
                                </div>
                            </div>
                            <div class="temperatura-box">
                                <span style="color: #000; font-size: 10px;">risco: </span>
                                <div class="risco" style="background-color:{col};">
                                    <div class="text-value">{line.get('risco', 0)} %</div>
                                </div>
                            </div>

                        </div>
                    </div>
                </div>"""
        
        html += """
                </div>
            </div>
        </div>"""
        
        return html
    
    def html(self):
        html = ''
        for line in self.render().split('\n'):
            html += line.strip()
        # print('--------------------------------')
        # print(html)
        return html