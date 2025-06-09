class CardTemperature:
    def __init__(self, title, tempo, lines):
        self.title = title
        self.tempo = tempo
        self.lines = lines    

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
        
        for line in self.lines:
            html += f"""
                <div class="container-temperatura">
                    <div class="describe">
                        <div class="mancal-guia">{line['nome']}</div>
                    </div>
                    <div class="bar">
                        <div class="bar-temp">"""
            
            for historico in line['historico'].items():
                html += f"""
                        <div class="bars" style="height: {historico[1]}px;">
                            <div class="rectangle" style="height: {historico[1]}px;"></div>
                            <div class="ellipse"></div>
                            <div class="time-label">{historico[0]}</div>
                        </div>"""
            
            html += f"""
                        </div>
                        <div class="temperaturas">
                            <div class="atual">
                                <div class="text-value">{line['atual']} °C</div>
                            </div>
                            <div class="alarme">
                                <div class="text-value">{line['alarme']} °C</div>
                            </div>
                            <div class="trip">
                                <div class="text-value">{line['trip']} °C</div>
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
        return html


# <!-- Bar 1 -->
# <div class="bars" style="height: 43px;">
# <div class="rectangle" style="height: 30px;"></div>
# <div class="ellipse"></div>
# <div class="time-label">12:20</div>
# </div>
# <!-- Bar 2 -->
# <div class="bars" style="height: 38px;">
# <div class="rectangle" style="height: 25px;"></div>
# <div class="ellipse"></div>
# <div class="time-label">12:21</div>
# </div>
# <!-- Bar 3 -->
# <div class="bars" style="height: 27px;">
# <div class="rectangle" style="height: 14px;"></div>
# <div class="ellipse"></div>
# <div class="time-label">12:22</div>
# </div>
# <!-- Bar 4 -->
# <div class="bars" style="height: 47px;">
# <div class="rectangle" style="height: 34px;"></div>
# <div class="ellipse"></div>
# <div class="time-label">12:23</div>
# </div>
# <!-- Bar 5 -->
# <div class="bars" style="height: 36px;">
# <div class="rectangle" style="height: 23px;"></div>
# <div class="ellipse"></div>
# <div class="time-label">12:24</div>
# </div>
# <!-- Bar 6 -->
# <div class="bars" style="height: 32px;">
# <div class="rectangle" style="height: 19px;"></div>
# <div class="ellipse"></div>
# <div class="time-label">12:25</div>
# </div>
# <!-- Bar 7 -->
# <div class="bars" style="height: 36px;">
# <div class="rectangle" style="height: 23px;"></div>
# <div class="ellipse"></div>
# <div class="time-label">12:26</div>
# </div>
# </div>