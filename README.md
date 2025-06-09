## DASHBOARD COG ENGESEP
''''
Objetivo: Visualizar de forma dinâmica as principais informações de um conjunto de Usinas Hidroelétricas.
Descrição geral de uma usina hidroelétrica (do ponto de vista de operação):
A usina controla o fluxo de água do reservatório através de comportas.
Esta água gira as turbinas, que acionam os geradores.
Os geradores convertem a energia mecânica em eletricidade.
Operadores monitoram níveis, vazões e produção,
ajustando a geração para atender à demanda e otimizar o uso da água.

''''
'''
Paginas
    Tela principal: 
        Objetivo: Mostrar as principais informações das usinas, que são:
            1. Unidade geradora
'''

---

## Estrutura do Projeto

```
16_interface_flask/
├── main.py                # Inicializa a aplicação Flask, SocketIO e observador de arquivos
├── prompt.py              # Utilitário para explorar a estrutura de arquivos e métodos do projeto
├── README.md              # Documentação do projeto
├── models/                # Lógica de acesso a dados, configuração e reset de alarmes
│   ├── config.py          # Configurações e mapeamento das usinas e CLPs
│   ├── load_data.py       # Funções para buscar e enviar dados das usinas
│   └── reset_alarmes.py   # Função para reset automático de alarmes
├── components/            # Componentes de visualização (cards de potência e temperatura)
│   ├── potencia_ativa.py  # Card para exibir potência ativa das usinas
│   └── temperaturas.py    # Card para exibir temperaturas das usinas
├── routes/                # Rotas Flask da aplicação
│   └── routes.py          # Define as rotas principais e streaming de dados
├── static/                # Arquivos estáticos (CSS, JS, imagens)
│   ├── css/               # Estilos customizados
│   ├── js/                # Scripts JavaScript (vazio)
│   └── imgs/              # Imagens (vazio)
├── templates/             # Templates HTML Jinja2
│   ├── base.html          # Template base
│   ├── index.html         # Página principal
│   └── temperaturas.html  # Página/fragmento de temperaturas
└── amv/                   # Ambiente virtual Python (dependências)
```

### Descrição dos principais arquivos/pastas

- **main.py**: Ponto de entrada da aplicação. Inicializa o Flask, SocketIO para comunicação em tempo real e um observador para recarregar a interface ao alterar arquivos estáticos/templates.
- **prompt.py**: Script utilitário para explorar a estrutura de arquivos, métodos e bibliotecas do projeto.
- **models/**: Contém a lógica de acesso a dados, configuração das usinas e funções auxiliares.
  - **config.py**: Define as configurações das usinas, CLPs, endereços IP, portas e mapeamento de variáveis.
  - **load_data.py**: Funções para buscar e enviar dados das usinas, incluindo integração com APIs e manipulação de DataFrames.
  - **reset_alarmes.py**: Função para reset automático de alarmes das usinas.
- **components/**: Componentes de visualização para a interface.
  - **potencia_ativa.py**: Card para exibir a potência ativa das usinas.
  - **temperaturas.py**: Card para exibir temperaturas e status térmico das usinas.
- **routes/**: Define as rotas Flask da aplicação.
  - **routes.py**: Rotas principais, incluindo a página inicial e streaming de dados em tempo real.
- **static/**: Arquivos estáticos usados pela interface.
  - **css/**: Estilos customizados (ex: style.css, variables.css).
  - **js/**: Scripts JavaScript (atualmente vazio).
  - **imgs/**: Imagens utilizadas na interface (atualmente vazio).
- **templates/**: Templates HTML baseados em Jinja2.
  - **base.html**: Template base para as páginas.
  - **index.html**: Página principal do dashboard.
  - **temperaturas.html**: Fragmento/página para exibir temperaturas.
- **amv/**: Ambiente virtual Python com dependências do projeto.

---
'''
# Requisitos do Dashboard COG - PCH/CGH

## 1. Visão Geral do Sistema

### 1.1 Objetivo
Desenvolver um dashboard web responsivo para monitoramento e controle de operações de Pequenas Centrais Hidrelétricas (PCH) e Centrais Geradoras Hidrelétricas (CGH), centralizando informações operacionais em tempo real através de múltiplas conexões API.

### 1.2 Escopo
Sistema de supervisão e controle para operadores de centrais hidrelétricas, permitindo monitoramento contínuo, análise de desempenho e tomada de decisões operacionais.

## 2. Requisitos Funcionais

### 2.1 Monitoramento em Tempo Real

#### 2.1.1 Dados Operacionais
- *RF001*: Exibir potência ativa gerada (MW) por unidade geradora
- *RF002*: Mostrar potência reativa (MVAr) e fator de potência
- *RF003*: Apresentar tensão, corrente e frequência dos geradores
- *RF004*: Monitorar nível d'água do reservatório/canal de adução
- *RF005*: Exibir vazão turbinada e vazão afluente
- *RF006*: Mostrar abertura das comportas e posição dos equipamentos
- *RF007*: Apresentar temperatura dos mancais e óleo dos transformadores

#### 2.1.2 Status dos Equipamentos
- *RF008*: Indicar status operacional (Operando/Parado/Manutenção) de cada unidade
- *RF009*: Exibir alarmes ativos e histórico de eventos
- *RF010*: Mostrar disponibilidade e confiabilidade dos equipamentos
- *RF011*: Apresentar horas de operação e próximas manutenções programadas

### 2.2 Visualização de Dados

#### 2.2.1 Dashboards Principais
- *RF012*: Dashboard executivo com KPIs consolidados
- *RF013*: Visão operacional detalhada por usina
- *RF014*: Painel de alarmes e eventos críticos
- *RF015*: Dashboard de performance e eficiência energética

#### 2.2.2 Gráficos e Relatórios
- *RF016*: Gráficos de tendência histórica (1h, 24h, 7d, 30d)
- *RF017*: Curvas de carga e geração
- *RF018*: Comparativo de performance entre usinas
- *RF019*: Relatórios automáticos de produção diária/mensal

### 2.3 Controle e Comando

#### 2.3.1 Comandos Remotos
- *RF020*: Liga/desliga unidades geradoras (com confirmação dupla)
- *RF021*: Ajuste de potência ativa/reativa dentro dos limites
- *RF022*: Controle de comportas (abertura/fechamento)
- *RF023*: Reset de proteções e alarmes não críticos
- *RF024*: Sincronização com o sistema elétrico

#### 2.3.2 Controles de Segurança
- *RF025*: Autenticação multi-fator para comandos críticos
- *RF026*: Log auditável de todas as ações de controle
- *RF027*: Bloqueio de comandos conflitantes
- *RF028*: Modo de emergência com comandos prioritários

### 2.4 Gestão de Alarmes

#### 2.4.1 Sistema de Alertas
- *RF029*: Classificação de alarmes por criticidade (Crítico/Alto/Médio/Baixo)
- *RF030*: Notificações por email, SMS e push notifications
- *RF031*: Escalação automática de alarmes não reconhecidos
- *RF032*: Filtros personalizáveis de alarmes por usuário/perfil

#### 2.4.2 Análise de Eventos
- *RF033*: Correlação automática de eventos relacionados
- *RF034*: Sugestões de ações corretivas baseadas no histórico
- *RF035*: Relatórios de análise de causa raiz
- *RF036*: Indicadores de tempo médio de resposta a alarmes

### 2.5 Análise e Otimização

#### 2.5.1 Performance Energética
- *RF037*: Cálculo de eficiência energética por unidade
- *RF038*: Análise de perdas no sistema de transmissão
- *RF039*: Otimização automática de despacho entre unidades
- *RF040*: Previsão de geração baseada em dados hidrológicos

#### 2.5.2 Manutenção Preditiva
- *RF041*: Análise de vibração e temperatura para manutenção preditiva
- *RF042*: Indicadores de saúde dos equipamentos
- *RF043*: Cronograma otimizado de manutenções
- *RF044*: Gestão de estoque de peças críticas

## 3. Requisitos de Integração API

### 3.1 Conectividade
- *RNF001*: Suporte a múltiplos protocolos: REST API, MQTT, OPC UA, Modbus TCP
- *RNF002*: Conexões simultâneas com até 50 endpoints diferentes
- *RNF003*: Reconnexão automática em caso de falha de comunicação
- *RNF004*: Buffer local para dados durante indisponibilidade de rede

### 3.2 Fontes de Dados
- *RNF005*: Integração com SCADA das usinas
- *RNF006*: Conexão com sistemas ERP para dados comerciais
- *RNF007*: Interface com ONS (Operador Nacional do Sistema)
- *RNF008*: Integração com sistemas meteorológicos e hidrológicos
- *RNF009*: Conexão com laboratórios de análise de óleo e vibração

### 3.3 Formato de Dados
- *RNF010*: Suporte a JSON, XML e CSV
- *RNF011*: Normalização automática de unidades de medida
- *RNF012*: Validação e limpeza de dados inconsistentes
- *RNF013*: Compressão de dados históricos

## 4. Requisitos Não Funcionais

### 4.1 Performance
- *RNF014*: Tempo de resposta < 2 segundos para consultas em tempo real
- *RNF015*: Atualização de dados críticos a cada 5 segundos
- *RNF016*: Suporte a 100 usuários simultâneos
- *RNF017*: Disponibilidade de 99.9% (8.77 horas de downtime/ano)

### 4.2 Segurança
- *RNF018*: Criptografia end-to-end para todas as comunicações
- *RNF019*: Autenticação via Active Directory/LDAP
- *RNF020*: Controle de acesso baseado em perfis (RBAC)
- *RNF021*: Audit trail completo de todas as ações
- *RNF022*: Backup automático diário com retenção de 7 anos

### 4.3 Usabilidade
- *RNF023*: Interface responsiva para desktop, tablet e mobile
- *RNF024*: Suporte a múltiplos idiomas (PT-BR, EN, ES)
- *RNF025*: Temas claro e escuro personalizáveis
- *RNF026*: Acessibilidade conforme WCAG 2.1 Level AA

### 4.4 Escalabilidade
- *RNF027*: Arquitetura baseada em microserviços
- *RNF028*: Deploy em containers Docker/Kubernetes
- *RNF029*: Banco de dados distribuído para big data
- *RNF030*: Cache distribuído para otimização de consultas

## 5. Requisitos de Infraestrutura

### 5.1 Ambiente de Produção
- *RNF031*: Deploy em nuvem híbrida (AWS/Azure + on-premises)
- *RNF032*: Redundância geográfica dos dados
- *RNF033*: Balanceamento de carga automático
- *RNF034*: Monitoramento de infraestrutura 24/7

### 5.2 Banco de Dados
- *RNF035*: Banco de dados de séries temporais para dados operacionais
- *RNF036*: Banco relacional para dados de configuração
- *RNF037*: Data lake para análises avançadas e machine learning
- *RNF038*: Retenção de dados por 10 anos para dados críticos

## 6. Requisitos Regulatórios

### 6.1 Conformidade Setor Elétrico
- *RNF039*: Conformidade com os Procedimentos de Rede do ONS
- *RNF040*: Atendimento aos requisitos da ANEEL para PCH/CGH
- *RNF041*: Registros conforme Submódulo 15.6 do ONS
- *RNF042*: Relatórios automáticos para órgãos reguladores

### 6.2 Padrões Técnicos
- *RNF043*: Conformidade com IEC 61850 para comunicação
- *RNF044*: Aderência aos padrões IEEE para sistemas elétricos
- *RNF045*: Certificação ISO 27001 para segurança da informação
- *RNF046*: Conformidade com LGPD para proteção de dados

## 7. Matriz de Priorização

### Prioridade Alta (Essencial)
- Monitoramento em tempo real (RF001-RF011)
- Dashboards principais (RF012-RF015)
- Sistema de alarmes (RF029-RF032)
- Conectividade API (RNF001-RNF004)
- Performance e segurança básica (RNF014-RNF021)

### Prioridade Média (Importante)
- Controle remoto (RF020-RF028)
- Análise de performance (RF037-RF040)
- Relatórios avançados (RF016-RF019)
- Manutenção preditiva (RF041-RF044)
- Escalabilidade (RNF027-RNF030)

### Prioridade Baixa (Desejável)
- Funcionalidades avançadas de IA
- Integração com sistemas legados específicos
- Personalizações por cliente
- Módulos de treinamento integrados

## 8. Cronograma Sugerido

### Fase 1 (3 meses): MVP
- Dashboards básicos de monitoramento
- Integração com 3-5 APIs principais
- Sistema básico de alarmes
- Deploy em ambiente de desenvolvimento

### Fase 2 (2 meses): Operacional
- Controles remotos básicos
- Sistema completo de alarmes
- Performance otimizada
- Deploy em ambiente de homologação

### Fase 3 (3 meses): Avançado
- Análises preditivas
- Otimização automática
- Relatórios regulatórios
- Deploy em produção

### Fase 4 (2 meses): Expansão
- Funcionalidades avançadas
- Integrações adicionais
- Otimizações baseadas no uso
- Documentação completa
'''