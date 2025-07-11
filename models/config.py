leituras = {
    "CGH APARECIDA": {
        "ip": "100.110.212.125",
        # "ip": "192.168.0.124",
        "port": 8010,
        "table": "cgh_aparecida",
        "CLPS":{
            "UG-01": {
                'conexao': {'ip': '192.168.10.2', 'port': 502}, 
                # 'conexao': {'ip': '192.168.1.2', 'port': 502}, 
                'caracteristicas': {
                    'potência máxima': 3650,
                    'velocidade máxima': 450,
                },
                'leituras': {
                    # "REAL": { "Potência Ativa Acumulada": 13241, "Nível Montante": 13519, "Nível Jusante": 13521},
                    "INT": { "Potência Ativa": 13407, "Turbina Velocidade": 13321},
                },
                "temperaturas":{
                    "REAL": {
                        "Enrolamento Fase A": {
                            'value': 13469,
                            'alarm_config': { 'register': 13989, 'criticidade': 'Média' },
                            'trip_config': { 'register': 13925, 'criticidade': 'Crítica' },
                            'alarm_threshold_value': 80.0,
                            'trip_threshold_value': 90.0
                        },
                        "Enrolamento Fase B": {
                            'value': 13471,
                            'alarm_config': { 'register': 13991, 'criticidade': 'Média' },
                            'trip_config': { 'register': 13927, 'criticidade': 'Crítica' },
                            'alarm_threshold_value': 80.0,
                            'trip_threshold_value': 90.0
                        },
                        "Enrolamento Fase C": {
                            'value': 13473,
                            'alarm_config': { 'register': 13993, 'criticidade': 'Média' },
                            'trip_config': { 'register': 13929, 'criticidade': 'Crítica' },
                            'alarm_threshold_value': 80.0,
                            'trip_threshold_value': 90.0
                        },
                    }
                },
                "alarmes":{
                    "BOOLEAN": {
                        "[01.00] - PCP-U1 - Botão de Emergência Acionado": { "register": 24289, "criticidade": "Alta" },
                        "[01.01] - PCP-U1 - Botão de Emergência Acionado - SuperSEP": { "register": 24290, "criticidade": "Crítica" }
                    }
                },
                "comandos":{
                    "BOOLEAN": {
                        "Reset SuperSEP": 12850,
                        "CalaSirene SuperSEP": 12852,
                        "Reset local": 12849,
                    }
                },
                "alarmes_reset_automatico":{
                    "BOOLEAN": {
                        "[01.00] - PCP-U1 - Botão de Emergência Acionado": 24289,
                    }
                },
                
            },
        }
    },
    "CGH FAE": {
        "ip": "100.106.33.66",
        "port": 8010,
        "table": "cgh_fae",
        "CLPS":{
            "UG-01": {
                'conexao': {'ip': '192.168.10.2', 'port': 502}, 
                'caracteristicas': {
                    'potência máxima': 1350,
                    'velocidade máxima': 415,
                },
                'leituras': {
                        "REAL": {
                            "Potência Ativa": 13407, 
                            # "Potência Ativa Acumulada": 13541, 
                            # "Turbina Velocidade": 13321
                        },
                        # "INT": {},
                },
                "temperaturas":{
                    "REAL": {
                            "Enrolamento Fase A": {
                                'value': 13455,
                                'alarm_config': { 'register': 13975, 'criticidade': 'Média' },
                                'trip_config': { 'register': 13911, 'criticidade': 'Crítica' },
                                'alarm_threshold_value': 75.0,
                                'trip_threshold_value': 85.0
                            },
                            "Enrolamento Fase B": {
                                'value': 13457,
                                'alarm_config': { 'register': 13977, 'criticidade': 'Média' },
                                'trip_config': { 'register': 13913, 'criticidade': 'Crítica' },
                                'alarm_threshold_value': 75.0,
                                'trip_threshold_value': 85.0
                            },
                            "Enrolamento Fase C": {
                                'value': 13459,
                                'alarm_config': { 'register': 13979, 'criticidade': 'Média' },
                                'trip_config': { 'register': 13915, 'criticidade': 'Crítica' },
                                'alarm_threshold_value': 75.0,
                                'trip_threshold_value': 85.0
                            },
                        },
                    },
                # },
                "alarmes":{
                    "BOOLEAN": {
                        "[01.00] - PCP-U1 - Botão de Emergência Acionado": { "register": 24289, "criticidade": "Alta" },
                        "[01.01] - PCP-U1 - Botão de Emergência Acionado - SuperSEP": { "register": 24290, "criticidade": "Crítica" }
                    }
                },
                "comandos":{
                    "BOOLEAN": {
                        "Reset SuperSEP": 12529,
                        "CalaSirene SuperSEP": 12532,
                        "LIGAR_UNIDADE": 1001,
                        "DESLIGAR_UNIDADE": 1002
                    },
                    "REAL": {
                        "AJUSTAR_POTENCIA": 2001
                    }
                }
            },
            "UG-02": {
                'conexao': {'ip': '192.168.10.3', 'port': 502},
                'caracteristicas': {
                    'potência máxima': 650,
                    'velocidade máxima': 800,
                },
                'leituras': {
                        "REAL": {
                            "Potência Ativa": 13407, 
                            # "Potência Ativa Acumulada": 13541, 
                            # "Turbina Velocidade": 13321
                        },
                        # "INT": {},
                },
                "temperaturas":{
                    "REAL": {
                            "Enrolamento Fase A": {
                                'value': 13455,
                                'alarmes': 13975,
                                'trip': 13911,
                            },
                            "Enrolamento Fase B": {
                                'value': 13457,
                                'alarmes': 13977,
                                'trip': 13913,
                            },
                            "Enrolamento Fase C": {
                                'value': 13459,
                                'alarmes': 13979,
                                'trip': 13915,
                            },
                        },
                    },
                # },
                "alarmes":{
                    "BOOLEAN": {
                        "[01.00] - PCP-U1 - Botão de Emergência Acionado": 24289,
                        "[01.01] - PCP-U1 - Botão de Emergência Acionado - SuperSEP": 24290,
                    }
                },
                "comandos":{
                    "BOOLEAN": {
                        "Reset SuperSEP": 12529,
                        "CalaSirene SuperSEP": 12532,
                    }
                }
            },
            # "PSA": {
            #     'conexao': {'ip': '192.168.10.4', 'port': 502}, 
            #     'leituras': {
            #             "REAL": {
            #                 "Nível Montante": 13353, 
            #                 "Nível Jusante": 13379
            #             },
            #             # "INT": {},
            #     },
            #     "alarmes":{
            #             "BOOLEAN": {
            #                 "[01.00]: PSA - Falha de Acionamento - KRD - Tensão no Serviço Auxiliar - Linha 23,1 kV - Alarme": 24289,
            #                 "[01.01]: PSA - Falha de Acionamento - KRD - Tensão no Serviço Auxiliar - Linha 23,1 kV - Trip": 24290,
            #             }
            #     },
            #     "comandos":{
            #             "BOOLEAN": {
            #                 "Reset SuperSEP": 12450,
            #             }
            #     }
            # }
        },
    },
    "CGH DAS PEDRAS": {
        "ip": "100.93.237.40",
        "port": 8010,
        "table": "cgh_das_pedras",
        "CLPS":{
            "UG-01": {
                'conexao': {'ip': '192.168.10.2', 'port': 502}, 
                'caracteristicas': {
                    'potência máxima': 3000,
                    'velocidade máxima': 450,
                },
                'leituras': {
                        "REAL": {
                            "Potência Ativa": 13407, 
                            # "Potência Ativa Acumulada": 13541, 
                            # "Turbina Velocidade": 13321
                        },
                        # "INT": {},
                },
                "temperaturas":{
                    "REAL": {
                        "Enrolamento Fase A": {
                            'value': 13459,
                            'alarmes': 13979,
                            'trip': 13915,
                        },
                        "Enrolamento Fase B": {
                            'value': 13461,
                            'alarmes': 13981,
                            'trip': 13917,
                        },
                        "Enrolamento Fase C": {
                            'value': 13463,
                            'alarmes': 13983,
                            'trip': 13919,
                        },
                    },
                },
                "alarmes":{
                    "BOOLEAN": {
                        "[01.00] - PCP-U1 - Botão de Emergência Acionado": 24289,
                        "[01.01] - PCP-U1 - Botão de Emergência Acionado - SuperSEP": 24290,
                    }
                },
                "comandos":{
                    "BOOLEAN": {
                        "Reset SuperSEP": 12529,
                        "CalaSirene SuperSEP": 12532,
                    }
                }
            },
            "UG-02": {
                'conexao': {'ip': '192.168.10.3', 'port': 502}, 
                'caracteristicas': {
                    'potência máxima': 3650,
                    'velocidade máxima': 450,
                },
                'leituras': {
                        "REAL": {
                            "Potência Ativa": 13407, 
                            # "Potência Ativa Acumulada": 13541, 
                            # "Turbina Velocidade": 13321
                        },
                        # "INT": {},
                },
                "temperaturas":{
                    "REAL": {
                        "Enrolamento Fase A": {
                            'value': 13459,
                            'alarmes': 13979,
                            'trip': 13915,
                        },
                        "Enrolamento Fase B": {
                            'value': 13461,
                            'alarmes': 13981,
                            'trip': 13917,
                        },
                        "Enrolamento Fase C": {
                            'value': 13463,
                            'alarmes': 13983,
                            'trip': 13919,
                        },
                    },
                },
                "alarmes":{
                    "BOOLEAN": {
                        "[01.00] - PCP-U1 - Botão de Emergência Acionado": 24289,
                        "[01.01] - PCP-U1 - Botão de Emergência Acionado - SuperSEP": 24290,
                    }
                },
                "comandos":{
                    "BOOLEAN": {
                        "Reset SuperSEP": 12529,
                        "CalaSirene SuperSEP": 12532,
                    }
                }
            },
        }
    },
    "CGH PICADAS ALTAS": {
        "ip": "100.79.241.13",
        "port": 8010,
        "table": "cgh_picadas_altas",
        "CLPS":{
            "UG-01": {
                'conexao': {'ip': '192.168.10.2', 'port': 502}, 
                'caracteristicas': {
                    'potência máxima': 3000,
                    'velocidade máxima': 450,
                },
                'leituras': {
                        "REAL": {
                            "Potência Ativa": 13407, 
                            # "Potência Ativa Acumulada": 13541, 
                            # "Turbina Velocidade": 13321
                        },
                        # "INT": {},
                },
                "alarmes":{
                    "BOOLEAN": {
                        "[01.00] - PCP-U1 - Botão de Emergência Acionado": 24289,
                        "[01.01] - PCP-U1 - Botão de Emergência Acionado - SuperSEP": 24290,
                    }
                },
                "comandos":{
                    "BOOLEAN": {
                        "Reset SuperSEP": 12529,
                        "CalaSirene SuperSEP": 12532,
                    }
                }
            },
            "UG-02": {
                'conexao': {'ip': '192.168.10.3', 'port': 502}, 
                'caracteristicas': {
                    'potência máxima': 3650,
                    'velocidade máxima': 450,
                },
                'leituras': {
                        "REAL": {
                            "Potência Ativa": 13407, 
                            # "Potência Ativa Acumulada": 13541, 
                            # "Turbina Velocidade": 13321
                        },
                        # "INT": {},
                },
                "alarmes":{
                    "BOOLEAN": {
                        "[01.00] - PCP-U1 - Botão de Emergência Acionado": 24289,
                        "[01.01] - PCP-U1 - Botão de Emergência Acionado - SuperSEP": 24290,
                    }
                },
                "comandos":{
                    "BOOLEAN": {
                        "Reset SuperSEP": 12529,
                        "CalaSirene SuperSEP": 12532,
                    }
                }
            },
            # "PSA": {
            #     'conexao': {'ip': '192.168.10.4', 'port': 502}, 
            #     'leituras': {
            #             "REAL": {
            #                 "Nível Montante": 13353, 
            #                 "Nível Jusante": 13355
            #             },
            #             # "INT": {},
            #     },
            #     "alarmes":{
            #             "BOOLEAN": {
            #                 "[01.00]: PSA - Falha de Acionamento - KRD - Tensão no Serviço Auxiliar - Linha 23,1 kV - Alarme": 24289,
            #                 "[01.01]: PSA - Falha de Acionamento - KRD - Tensão no Serviço Auxiliar - Linha 23,1 kV - Trip": 24290,
            #             }
            #     },
            #     "comandos":{
            #             "BOOLEAN": {
            #                 "Reset SuperSEP": 12450,
            #             }
            #     }
            # }
        }
    },
    "CGH HOPPEN": {
        "ip": "100.73.37.105",
        "port": 8010,
        "table": "cgh_hoppen",
        "CLPS":{
            "UG-01": {
                'conexao': {'ip': '192.168.10.2', 'port': 502}, 
                'caracteristicas': {
                    'potência máxima': 1300,
                    'velocidade máxima': 415,
                },
                'leituras': {
                        "REAL": {
                            "Potência Ativa": 13407, 
                            # "Potência Ativa Acumulada": 13541, 
                            # "Turbina Velocidade": 13321
                        },
                        # "INT": {},
                },
                "alarmes":{
                    "BOOLEAN": {
                        "[01.00] - PCP-U1 - Botão de Emergência Acionado": 24289,
                        "[01.01] - PCP-U1 - Botão de Emergência Acionado - SuperSEP": 24290,
                    }
                },
                "comandos":{
                    "BOOLEAN": {
                        "Reset SuperSEP": 12529,
                        "CalaSirene SuperSEP": 12532,
                    }
                }
            },
            "UG-02": {
                'conexao': {'ip': '192.168.10.3', 'port': 502}, 
                'caracteristicas': {
                    'potência máxima': 1300,
                    'velocidade máxima': 415,
                },
                'leituras': {
                        "REAL": {
                            "Potência Ativa": 13407, 
                            # "Potência Ativa Acumulada": 13541, 
                            # "Turbina Velocidade": 13321
                        },
                        # "INT": {},
                },
                "alarmes":{
                    "BOOLEAN": {
                        "[01.00] - PCP-U1 - Botão de Emergência Acionado": 24289,
                        "[01.01] - PCP-U1 - Botão de Emergência Acionado - SuperSEP": 24290,
                    }
                },
                "comandos":{
                    "BOOLEAN": {
                        "Reset SuperSEP": 12529,
                        "CalaSirene SuperSEP": 12532,
                    }
                }
            },
            # "PSA": {
            #     'conexao': {'ip': '192.168.10.4', 'port': 502}, 
            #     'leituras': {
            #             "REAL": {
            #                 "Nível Montante": 13353, 
            #                 "Nível Jusante": 13355
            #             },
            #             # "INT": {},
            #     },
            #     "alarmes":{
            #             "BOOLEAN": {
            #                 "[01.00]: PSA - Falha de Acionamento - KRD - Tensão no Serviço Auxiliar - Linha 23,1 kV - Alarme": 24289,
            #                 "[01.01]: PSA - Falha de Acionamento - KRD - Tensão no Serviço Auxiliar - Linha 23,1 kV - Trip": 24290,
            #             }
            #     },
            #     "comandos":{
            #             "BOOLEAN": {
            #                 "Reset SuperSEP": 12450,
            #             }
            #     }
            # }
        }
    }
}