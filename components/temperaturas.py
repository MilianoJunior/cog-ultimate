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
            # --- SVG Chart Rendering ---
            svg_width = 280
            svg_height = 100
            padding = 20 # Padding around the chart for labels/axes
            chart_width = svg_width - 2 * padding
            chart_height = svg_height - 2 * padding

            historico_data = line.get('historico_list', []) # List of (timestamp, value)

            # Prepare data points, ensuring values are numeric
            points = []
            valid_values = []
            if historico_data:
                for ts, val in historico_data:
                    if val is not None:
                        try:
                            points.append((float(ts), float(val)))
                            valid_values.append(float(val))
                        except (ValueError, TypeError):
                            continue # Skip non-numeric data

            if not points:
                svg_chart_html = f'<svg width="{svg_width}" height="{svg_height}" class="temp-chart-svg"><text x="{svg_width/2}" y="{svg_height/2}" text-anchor="middle" fill="#888">Sem dados históricos</text></svg>'
            else:
                # Determine data ranges
                min_ts = points[0][0]
                max_ts = points[-1][0]

                # Temperature range: consider alarm/trip lines and data range
                min_val_data = min(valid_values) if valid_values else 0
                max_val_data = max(valid_values) if valid_values else 100 # default if no data

                # Ensure alarm/trip lines are visible, extend range slightly
                alarm_val = float(line.get('alarme', 0)) # Numeric threshold
                trip_val = float(line.get('trip', 0))   # Numeric threshold

                min_y_display = min(0, min_val_data, alarm_val - 10 if alarm_val else float('inf'))
                max_y_display = max(max_val_data + 10, trip_val + 10 if trip_val else -float('inf'), alarm_val +10 if alarm_val else -float('inf'))
                if max_y_display <= min_y_display : # Avoid division by zero if all values are same or flat
                    max_y_display = min_y_display + 20


                # Scaling functions
                def scale_x(ts):
                    if max_ts == min_ts: # Avoid division by zero if only one point
                        return padding + chart_width / 2
                    return padding + ((ts - min_ts) / (max_ts - min_ts)) * chart_width

                def scale_y(val):
                    if max_y_display == min_y_display: # Avoid division by zero
                        return padding + chart_height / 2
                    return padding + chart_height - ((val - min_y_display) / (max_y_display - min_y_display)) * chart_height

                polyline_points = " ".join([f"{scale_x(ts)},{scale_y(val)}" for ts, val in points])

                svg_chart_html = f'<svg width="{svg_width}" height="{svg_height}" class="temp-chart-svg">'
                # Background rectangle (optional)
                # svg_chart_html += f'<rect x="0" y="0" width="{svg_width}" height="{svg_height}" fill="#f9f9f9" />'

                # X-axis (simple line)
                svg_chart_html += f'<line x1="{padding}" y1="{padding + chart_height}" x2="{padding + chart_width}" y2="{padding + chart_height}" stroke="#ccc" stroke-width="1"/>'
                # Y-axis (simple line)
                svg_chart_html += f'<line x1="{padding}" y1="{padding}" x2="{padding}" y2="{padding + chart_height}" stroke="#ccc" stroke-width="1"/>'

                # Alarm line
                if line.get('alarme') is not None:
                    y_alarm = scale_y(alarm_val)
                    svg_chart_html += f'<line x1="{padding}" y1="{y_alarm}" x2="{padding + chart_width}" y2="{y_alarm}" stroke="orange" stroke-width="1" stroke-dasharray="4 2"/>'
                    svg_chart_html += f'<text x="{padding + chart_width + 2}" y="{y_alarm + 3}" font-size="10" fill="orange">Alarme ({alarm_val}°C)</text>'


                # Trip line
                if line.get('trip') is not None:
                    y_trip = scale_y(trip_val)
                    svg_chart_html += f'<line x1="{padding}" y1="{y_trip}" x2="{padding + chart_width}" y2="{y_trip}" stroke="red" stroke-width="1" stroke-dasharray="4 2"/>'
                    svg_chart_html += f'<text x="{padding + chart_width + 2}" y="{y_trip + 3}" font-size="10" fill="red">Trip ({trip_val}°C)</text>'

                # Data polyline
                svg_chart_html += f'<polyline points="{polyline_points}" fill="none" stroke="#50C9F6" stroke-width="2"/>'

                # Data points (circles)
                for ts, val in points:
                    svg_chart_html += f'<circle cx="{scale_x(ts)}" cy="{scale_y(val)}" r="2" fill="#50C9F6"/>'

                svg_chart_html += '</svg>'

            html += f"""
                <div class="container-temperatura">
                    <div class="describe">
                        <div class="mancal-guia">{line['nome']}</div>
                    </div>
                    <div class="temp-chart-container">
                        {svg_chart_html}
                    </div>
                    <div class="temp-values-display">
                        <div class="atual">
                            <span class="label">Atual:</span>
                            <span class="value">{line.get('atual', 'N/A')} °C</span>
                        </div>
                        <div class="alarme-disp">
                            <span class="label">Alarme:</span>
                            <span class="value">{line.get('alarme', 'N/A')} °C</span>
                        </div>
                        <div class="trip-disp">
                            <span class="label">Trip:</span>
                            <span class="value">{line.get('trip', 'N/A')} °C</span>
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