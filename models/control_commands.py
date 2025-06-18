import asyncio
import logging
from typing import Any, Dict, Tuple, Union

from models.config import leituras
from models.load_data import set_data # Assuming set_data is async as per plan

# Helper type for the result
CommandResult = Tuple[bool, str]

# Get a logger instance for this module
logger = logging.getLogger(__name__)

def send_command(usina_id: str, unidade_id: str, comando_str_from_route: str, valor: Any = None) -> CommandResult:
    """
    Processes a command, looks up configuration, and sends it to the appropriate device
    using set_data.
    """
    logger.info(f"Tentativa de comando: Usina={usina_id}, Unidade={unidade_id}, Comando={comando_str_from_route}, Valor={valor}")

    usina_config = leituras.get(usina_id)
    if not usina_config:
        logger.error(f"Configuração da usina '{usina_id}' não encontrada.")
        return False, f"Configuração da usina '{usina_id}' não encontrada."

    clps_config = usina_config.get('CLPS', {})
    unidade_config = clps_config.get(unidade_id)
    if not unidade_config:
        logger.error(f"Configuração da unidade '{unidade_id}' na usina '{usina_id}' não encontrada.")
        return False, f"Configuração da unidade '{unidade_id}' na usina '{usina_id}' não encontrada."

    service_ip = usina_config.get('ip')
    service_port = usina_config.get('port')
    clp_connection_info = unidade_config.get('conexao')

    if not service_ip or not service_port or not clp_connection_info:
        logger.error(f"Informações de conexão incompletas para usina '{usina_id}' ou unidade '{unidade_id}'. IP={service_ip}, Port={service_port}, CLPConn={clp_connection_info}")
        return False, f"Informações de conexão incompletas para usina '{usina_id}' ou unidade '{unidade_id}'."

    logger.info(f"Info Usina para comando: IP={service_ip}, Porta={service_port}")
    logger.info(f"Info CLP para comando: {clp_connection_info}")

    registrador_nome_real = None
    registrador_endereco = None
    valor_a_escrever = None
    tipo_registrador = None

    comandos_config = unidade_config.get('comandos', {})
    logger.info(f"Comandos configurados para unidade '{unidade_id}': {comandos_config}")

    if comando_str_from_route == "LIGAR":
        registrador_nome_real = "LIGAR_UNIDADE"
        tipo_registrador = "BOOLEAN"
        valor_a_escrever = True
    elif comando_str_from_route == "DESLIGAR":
        registrador_nome_real = "DESLIGAR_UNIDADE"
        tipo_registrador = "BOOLEAN"
        valor_a_escrever = True
    elif comando_str_from_route == "AJUSTAR_POTENCIA":
        registrador_nome_real = "AJUSTAR_POTENCIA"
        tipo_registrador = "REAL"
        try:
            valor_a_escrever = float(valor) if valor is not None else None
            if valor_a_escrever is None:
                logger.error(f"Valor para AJUSTAR_POTENCIA não fornecido ou inválido para Usina={usina_id}, Unidade={unidade_id}. Valor recebido: {valor}")
                return False, "Valor para AJUSTAR_POTENCIA não fornecido ou inválido."
        except ValueError:
            logger.error(f"Valor para AJUSTAR_POTENCIA não é um número válido para Usina={usina_id}, Unidade={unidade_id}. Valor: {valor}")
            return False, f"Valor para AJUSTAR_POTENCIA não é um número válido: {valor}"
    else:
        logger.error(f"Comando '{comando_str_from_route}' desconhecido para Usina={usina_id}, Unidade={unidade_id}.")
        return False, f"Comando '{comando_str_from_route}' desconhecido."

    if tipo_registrador and registrador_nome_real:
        if tipo_registrador in comandos_config and registrador_nome_real in comandos_config[tipo_registrador]:
            registrador_endereco = comandos_config[tipo_registrador][registrador_nome_real]
        else:
            logger.error(f"Registrador '{registrador_nome_real}' do tipo '{tipo_registrador}' não encontrado na config de comandos para Usina={usina_id}, Unidade={unidade_id}. Comandos disponíveis: {comandos_config}")
            return False, f"Registrador '{registrador_nome_real}' não definido para a unidade '{unidade_id}'."

    if registrador_endereco is None:
        logger.error(f"Endereço do registrador para '{registrador_nome_real}' não pôde ser determinado para Usina={usina_id}, Unidade={unidade_id}.")
        # This typically means the previous checks failed and returned, but as a safeguard:
        return False, f"Endereço do registrador para '{registrador_nome_real}' não pôde ser determinado."

    logger.info(f"Mapeamento de comando: Rota='{comando_str_from_route}' -> Registrador Nome='{registrador_nome_real}', Endereço='{registrador_endereco}', Tipo='{tipo_registrador}', Valor a Escrever='{valor_a_escrever}' para Usina={usina_id}, Unidade={unidade_id}")

    config_param_set_data = {
        'ip': service_ip,
        'port': service_port,
        'tipo': tipo_registrador
    }
    data_param_set_data = {
        'conexao': clp_connection_info,
        tipo_registrador: {
            registrador_endereco: valor_a_escrever
        }
    }

    logger.info(f"Enviando comando para CLP: Usina={usina_id}, Unidade={unidade_id}, Registrador Endereço={registrador_endereco}, Valor={valor_a_escrever}, Tipo={tipo_registrador}, Config SetData={config_param_set_data}, Data SetData={data_param_set_data}")

    success_clp = False
    response_data_clp = None
    status_retorno = False
    mensagem_retorno = ""

    try:
        contador_simulado = 1
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        success_clp, response_data_clp = loop.run_until_complete(
            set_data(contador_simulado, usina_id, config_param_set_data, data_param_set_data)
        )
        loop.close()

        logger.info(f"Resultado do comando CLP (set_data): Sucesso={success_clp}, Resposta={response_data_clp} para Usina={usina_id}, Unidade={unidade_id}")

        if success_clp:
            status_retorno = True
            mensagem_retorno = f"Comando '{registrador_nome_real}' enviado com sucesso para {usina_id} - {unidade_id}. Resposta CLP: {response_data_clp}"
        else:
            status_retorno = False
            error_message_clp = response_data_clp.get('error', response_data_clp) if isinstance(response_data_clp, dict) else response_data_clp
            mensagem_retorno = f"Falha ao enviar comando '{registrador_nome_real}' para {usina_id} - {unidade_id}. Erro CLP: {error_message_clp}"
            logger.error(mensagem_retorno)

    except Exception as e:
        logger.critical(f"ERRO CRÍTICO ao chamar set_data ou processar seu resultado para Usina={usina_id}, Unidade={unidade_id}, Comando='{registrador_nome_real}': {e}", exc_info=True)
        status_retorno = False
        mensagem_retorno = f"Erro crítico interno ao executar comando: {e}"

    logger.info(f"Comando finalizado: Usina={usina_id}, Unidade={unidade_id}, Comando='{comando_str_from_route}', Sucesso={status_retorno}, Mensagem='{mensagem_retorno}'")
    return status_retorno, mensagem_retorno
