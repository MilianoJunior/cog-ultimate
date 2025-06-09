'''
    Resetar os alarmes automaticamente no CLP para evitar que seja necessário ficar apertando o botão de emergência.
'''
from models.load_data import set_current_values
from models.config import leituras

def reset_alarmes(usina):
    # config = leituras[usina]
    select_type = 'alarmes_reset_automatico'
    response = set_current_values(select_type)
    # for r in response:
    #     print('r: ', r['value'])
    # print('--------------------------------')
    

