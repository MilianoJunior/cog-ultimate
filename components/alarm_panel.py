import re

class AlarmPanel:
    """
    Component to display active alarms in a panel.
    """
    def __init__(self, active_alarms: list):
        self.active_alarms = active_alarms
        # Sort alarms by a predefined criticality order
        criticality_order = {
            "Crítica": 0,
            "Alta": 1,
            "Média": 2,
            "Aviso": 3, # Added "Aviso"
            "Baixa": 4,
            "Desconhecida": 5
        } # Lower number = higher priority
        self.active_alarms.sort(key=lambda x: criticality_order.get(x.get('criticidade', 'Desconhecida'), 99))


    def render(self) -> str:
        """
        Generates the HTML for the alarm panel.
        """
        filter_html = """
            <div class="alarm-filters">
                <select id="filter-usina">
                    <option value="all">Todas as Usinas</option>
                    {usina_options}
                </select>
                <select id="filter-unidade">
                    <option value="all">Todas as Unidades</option>
                    {unidade_options}
                </select>
                <select id="filter-criticidade">
                    <option value="all">Todas as Criticidades</option>
                    {criticidade_options}
                </select>
            </div>
        """

        if not self.active_alarms:
            # Still provide filters even if no alarms initially, they might come via SSE
            usinas = sorted(list(set(alarm.get('usina_id', 'N/A') for alarm in self.active_alarms if alarm.get('usina_id'))))
            unidades = sorted(list(set(alarm.get('unidade_id', 'N/A') for alarm in self.active_alarms if alarm.get('unidade_id'))))
            criticidades = sorted(list(set(alarm.get('criticidade', 'N/A') for alarm in self.active_alarms if alarm.get('criticidade'))))

            usina_opts_html = "".join(f'<option value="{u}">{u}</option>' for u in usinas)
            unidade_opts_html = "".join(f'<option value="{u}">{u}</option>' for u in unidades) # Simple population for now
            criticidade_opts_html = "".join(f'<option value="{c}">{c}</option>' for c in criticidades)

            filter_html = filter_html.format(
                usina_options=usina_opts_html,
                unidade_options=unidade_opts_html,
                criticidade_options=criticidade_opts_html
            )
            return filter_html + '<div class="alarm-panel-no-alarms"><p>Nenhum alarme ativo.</p></div>'

        # Populate filter options from available alarms
        usinas = sorted(list(set(alarm.get('usina_id', 'N/A') for alarm in self.active_alarms if alarm.get('usina_id'))))
        unidades = sorted(list(set(alarm.get('unidade_id', 'N/A') for alarm in self.active_alarms if alarm.get('unidade_id')))) # Could be refined based on selected usina
        criticidades = sorted(list(set(c for c in [alarm.get('criticidade') for alarm in self.active_alarms] if c and c != 'Desconhecida')  + ['Desconhecida']))


        usina_opts_html = "".join(f'<option value="{u}">{u}</option>' for u in usinas)
        unidade_opts_html = "".join(f'<option value="{u}">{u}</option>' for u in unidades) # Simple population for now

        # Ensure specific order for criticality if needed, or use sorted unique values
        # Adding "Aviso" to the standard order for filter population
        crit_order = ["Crítica", "Alta", "Média", "Aviso", "Baixa", "Desconhecida"]
        present_criticidades = set(alarm.get('criticidade', 'Desconhecida') for alarm in self.active_alarms)
        # Make sure all present_criticidades are in crit_order to avoid issues, or add them if not
        for pc in present_criticidades:
            if pc not in crit_order:
                crit_order.append(pc) # Add any other unknown type at the end

        criticidade_opts_html = "".join(f'<option value="{c}">{c}</option>' for c in crit_order if c in present_criticidades)


        filter_html = filter_html.format(
            usina_options=usina_opts_html,
            unidade_options=unidade_opts_html,
            criticidade_options=criticidade_opts_html
        )

        table_html = '<table class="alarm-table">'
        table_html += """
            <thead>
                <tr>
                    <th>Usina</th>
                    <th>Unidade</th>
                    <th>Descrição</th>
                    <th>Criticidade</th>
                </tr>
            </thead>
            <tbody id="alarm-table-body-content">
        """

        for alarm in self.active_alarms:
            usina = alarm.get('usina_id', 'N/A')
            unidade = alarm.get('unidade_id', 'N/A')
            descricao = alarm.get('descricao', 'Descrição não disponível')
            criticidade = alarm.get('criticidade', 'Desconhecida')

            criticidade_class = "criticidade-" + re.sub(r'\s+', '-', criticidade.lower())

            table_html += f"""
                <tr class="{criticidade_class}-row" data-usina="{usina}" data-unidade="{unidade}" data-criticidade="{criticidade}">
                    <td>{usina}</td>
                    <td>{unidade}</td>
                    <td>{descricao}</td>
                    <td class="{criticidade_class}">{criticidade}</td>
                </tr>
            """

        table_html += "</tbody></table>"
        return filter_html + table_html

    def html(self) -> str:
        """
        Renders the component and minifies its HTML output.
        """
        raw_html = self.render()
        # Minify HTML by removing unnecessary whitespace between tags and newlines
        minified_html = re.sub(r'>\s+<', '><', raw_html)
        minified_html = re.sub(r'\n\s*', '', minified_html)
        return minified_html.strip()

if __name__ == '__main__':
    # Example Usage (for testing the component directly)
    mock_alarms = [
        {'usina_id': 'CGH FAE', 'unidade_id': 'UG-01', 'descricao': 'Botão de Emergência Acionado', 'criticidade': 'Crítica'},
        {'usina_id': 'CGH APARECIDA', 'unidade_id': 'UG-01', 'descricao': 'Temperatura Alta Enrolamento A', 'criticidade': 'Alta'},
        {'usina_id': 'CGH FAE', 'unidade_id': 'UG-02', 'descricao': 'Falha na Comunicação SuperSEP', 'criticidade': 'Média'},
        {'usina_id': 'CGH HOPPEN', 'unidade_id': 'UG-01', 'descricao': 'Nível Baixo Reservatório', 'criticidade': 'Baixa'},
        {'usina_id': 'CGH TESTE', 'unidade_id': 'PSA', 'descricao': 'Alarme Genérico Teste', 'criticidade': 'Desconhecida'},
    ]
    alarm_panel = AlarmPanel(mock_alarms)
    print("Rendered HTML:\n", alarm_panel.render())
    print("\nMinified HTML:\n", alarm_panel.html())

    no_alarms_panel = AlarmPanel([])
    print("\nRendered HTML (No Alarms):\n", no_alarms_panel.render())
    print("\nMinified HTML (No Alarms):\n", no_alarms_panel.html())
