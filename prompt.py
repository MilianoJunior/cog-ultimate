import os
import ast

cont = 0
total_linhas = 0
count = 0



def estrutura_pastas_arquivos(caminho, prefixo="", imprimir=False):
    """
    Função recursiva que imprime o nome das pastas e o código dos arquivos Python, HTML, CSS e JavaScript encontrados.
    :param caminho: Caminho do diretório a ser listado.
    :param prefixo: Prefixo para formatação da saída.
    """
    global cont, total_linhas, count

    for item in os.listdir(caminho):
        item_path = os.path.join(caminho, item)
        list_exclude = ['__pycache__', '.idea', 'README.md', 'requirements.txt', 'prompt.py','__init__.py',
                        'socket.io.js','tests','.git','.cursor','test.py','amv']
        list_include = ['.py', '.html', '.css', '.js','.yaml']
        list_imprimir = ['.py','.html','.css','.js','.yaml']
        if item in list_exclude:
            continue

        if os.path.isdir(item_path):
            # Se o item é uma pasta, imprime o nome da pasta e faz a chamada recursiva
            cont += 1
            if not imprimir:
                print(f"{prefixo}{item}/")
            estrutura_pastas_arquivos(item_path, prefixo + "    ├── ", imprimir)
        elif os.path.isfile(item_path) and any([item.endswith(ext) for ext in list_include]):
            # Se o item é um arquivo Python, HTML, CSS ou JavaScript, imprime o nome do arquivo
            cont += 1
            if not imprimir:
                print(f"{prefixo}{item}")
                # print(f"{prefixo}├── {item}")
            if imprimir and any([item.endswith(ext) for ext in list_imprimir]):
                try:
                    with open(item_path, 'r', encoding='utf-8') as arquivo:
                        conteudo = arquivo.read()
                        count += 1
                        print('¨¨' * 50)
                        print(f'{count} - Conteúdo do arquivo {item}:')
                        print('¨¨' * 50)
                        print(conteudo)
                        total_linhas += len(conteudo.splitlines())
                        print(f'Quantidade de linhas do arquivo {item}: {len(conteudo.splitlines())} totalizando {total_linhas} linhas.')
                except UnicodeDecodeError:
                    try:
                        with open(item_path, 'r', encoding='latin1') as arquivo:
                            conteudo = arquivo.read()
                            count += 1
                            print('¨¨' * 50)
                            print(f'{count} - Conteúdo do arquivo {item}:')
                            print('¨¨' * 50)
                            print(conteudo)
                            total_linhas += len(conteudo.splitlines())
                            print(f'Quantidade de linhas do arquivo {item}: {len(conteudo.splitlines())} totalizando {total_linhas} linhas.')
                    except Exception as e:
                        print(f"Erro ao ler o arquivo {item}: {str(e)}")

def metodos_arquivos(caminho, prefixo=""):
    """
    Função recursiva que imprime os nomes das pastas e arquivos encontrados, e os métodos dos arquivos Python.
    """
    for item in os.listdir(caminho):
        item_path = os.path.join(caminho, item)

        list_exclude = ['__pycache__', '.idea', 'README.md', 'requirements.txt', 'prompt.py', '__init__.py',
                        'socket.io.js','tests','amv']
        list_include = ['.py', '.html', '.css', '.js']
        list_imprimir = ['.py']
        if item in list_exclude:
            continue

        if os.path.isdir(item_path):
            print(f"{prefixo}{item}/")
            metodos_arquivos(item_path, prefixo + "    ├── ")
        elif os.path.isfile(item_path) and any([item.endswith(ext) for ext in list_imprimir]):
            print(f"{prefixo}{item}")
            with open(item_path, 'r') as arquivo:
                conteudo = arquivo.read()
                tree = ast.parse(conteudo)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        print(f"{prefixo}    ├── Função: {node.name}")
                    elif isinstance(node, ast.ClassDef):
                        print(f"{prefixo}    ├── Classe: {node.name}")
                        for sub_node in node.body:
                            if isinstance(sub_node, ast.FunctionDef):
                                print(f"{prefixo}        ├── Método: {sub_node.name}")



def listar_bibliotecas(caminho):
    """
    Função que retorna todas as bibliotecas importadas nos arquivos Python do projeto.
    """
    bibliotecas = set()

    for root, _, files in os.walk(caminho):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    try:
                        tree = ast.parse(f.read(), filename=file_path)
                        for node in ast.walk(tree):
                            if isinstance(node, ast.Import):
                                for alias in node.names:
                                    bibliotecas.add(alias.name)
                            elif isinstance(node, ast.ImportFrom):
                                bibliotecas.add(node.module)
                    except SyntaxError:
                        print(f"Erro de sintaxe no arquivo: {file_path}")

    return bibliotecas

# Caminho do diretório do projeto
# caminho_projeto = os.getcwd()
# bibliotecas = listar_bibliotecas(caminho_projeto)
# print("Bibliotecas importadas no projeto:")
# for biblioteca in sorted(bibliotecas):
#     print(biblioteca)

# print('--' * 50)
# print('Estutura de pastas e arquivos do diretório atual:')
# print('--' * 50)
path = os.getcwd()
# # Execute the function to create the project structure
# # create_project_structure(path)
#
# estrutura_pastas_arquivos(path, "")
estrutura_pastas_arquivos(path, "")
print('-' * 50)
estrutura_pastas_arquivos(path, "", imprimir=True)
# print('-' * 50)
# print('Métodos e funções dos arquivos Python:')

# contador:  57 tempo_atual:  0.22269940376281738 tempo_total:  12.99897837638855  erros:  47 api versão 1
# contador:  57 tempo_atual:  0.12067461013793945 tempo_total:  7.112741470336914  erros:  1 api versão 2
# contador:  57 tempo_atual:  0.1147918701171875 tempo_total:  6.785559177398682 conta:  1 api versão 3

'''

## Rotas Disponíveis

### 1. `POST /readCLP/{tipo}`
- **Descrição:** Lê valores de registradores do CLP.
- **Parâmetro de rota:**
  - `tipo`: `leituras` ou `alarmes`
- **Body (JSON):**
  ```json
  {
    "conexao": {
      "ip": "192.168.0.10",
      "port": 502,
      "timeout": 10.0
    },
    "registers": {
      "REAL": {"nome1": 1001},
      "INT": {"nome2": 2001},
      "BOOLEAN": {"nome3": 3001}
    }
  }
  ```
- **Resposta (sucesso):**
  ```json
  {
    "data": {
      "REAL": {"nome1": 12.34},
      "INT": {"nome2": 42},
      "BOOLEAN": {"nome3": true}
    },
    "status": "success",
    "message": null
  }
  ```
- **Resposta (erro):**
  ```json
  {
    "data": null,
    "status": "error",
    "message": "Mensagem de erro"
  }
  ```

### 2. `POST /writeCLP/{tipo}`
- **Descrição:** Escreve valores em registradores do CLP (atualmente apenas para reset de alarmes automáticos).
- **Parâmetro de rota:**
  - `tipo`: `reset_alarmes_automatico`
- **Body (JSON):**
  ```json
  {
    "conexao": {
      "ip": "192.168.0.10",
      "port": 502,
      "timeout": 10.0
    },
    "registers": {
      "BOOLEAN": {"reset_alarme": [3001, true]}
    }
  }
  ```
- **Resposta (sucesso):**
  ```json
  {
    "data": {
      "BOOLEAN": {"reset_alarme": null}
    },
    "status": "success",
    "message": null
  }
  ```
- **Resposta (erro):**
  ```json
  {
    "data": null,
    "status": "error",
    "message": "Mensagem de erro"
  }
  ```

---

## Observações
- Os campos de conexão (`ip`, `port`, `timeout`) são obrigatórios.
- Os nomes dos registradores (`nome1`, `nome2`, etc.) são livres e servem apenas para identificar os dados no retorno.
- O tipo de dado deve ser especificado corretamente em `registers` (`REAL`, `INT`, `BOOLEAN`).
- Em caso de erro de conexão ou leitura/escrita, a resposta terá `status: error` e uma mensagem explicativa.

---

## Ambiente
- Assegure que o CLP esteja acessível via rede e que as portas estejam liberadas.
- Para ambientes de desenvolvimento, teste com CLPs simulados ou dispositivos reais.
'''

'''
Qual é o principal objetivo do seu COG, como prever falhas ou otimizar produção?
Esse resposta ainda não deve ser abordada, peço que releia a proposta incial, talvez para vc seja facil procurar essa resposta por que seu pensamento está considerando etapas que para vc já foram compreendidas.

Você prefere Flask ou está aberto a explorar opções mais robustas?
Tenho mais de 10 anos em experiência em python, essa opção deve considerar minha limitação de conhecimento.

Quais protocolos seus CLPs suportam, e como planeja proteger a VPN?
O protocolo suportado é Modbus TCP, e a VPN que vou usar é o tailscale, isso já esta defindo por causa de eu ser o unico desenvolvedor do projeto de software, custaria muito tempo apreender outras soluções.


Não vou responder essas perguntas, vc me parece muito impulsivo e prolixo, eu vou fazer as perguntas e vc responder.

Se vc não considerar essa regra, vou cancelar a conversa, vou ficar muito frustrado.

Regra: suas respostas devem ser curtas e não ter mais que 600 caracteres, com uma pergunta no final gerando um contexto lógico e não muito antecipado.

vou esperar sua resposta de confirmação e vou fazer a primeira pergunta.




Como você já tem um sistema em operação, gostaria de saber:

Quais são os principais desafios que você enfrenta hoje com o COG? Por exemplo, algo como prever falhas de equipamentos, gerenciar dados em tempo real ou otimizar o desempenho das operações?
O que, na sua visão, tornaria o processo mais "consciente"? Isso pode ser ter mais visibilidade sobre o que está acontecendo, tomar decisões mais rápidas ou reduzir desperdícios, por exemplo.
O que seria "agradável" para você nessa colaboração? Talvez seja evitar soluções muito complexas, ter liberdade para ajustar as ideias ou ver resultados práticos logo no início.




'''