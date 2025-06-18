import logging
from flask import Flask
# from livereload import Server
import os
from flask_socketio import SocketIO
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    handlers=[
        logging.FileHandler("command_audit.log"),
        # logging.StreamHandler() # Optionally add stream handler to see logs in console
    ]
)
logger = logging.getLogger(__name__)
logger.info("Aplicação iniciada e logger configurado.")

# Importa as rotas depois de criar a aplicação
from routes.routes import *

# Inicializa o SocketIO
socketio = SocketIO(app, cors_allowed_origins="*")

# Exemplo de evento para atualizar o cliente
@socketio.on('connect')
def handle_connect():
    pass

# Classe para lidar com eventos de mudança de arquivo
class ChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith('.css') or event.src_path.endswith('.html'):
            socketio.emit('atualizar', {'arquivo': event.src_path})

# Função para iniciar o observador
def start_observer():
    event_handler = ChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, path='.', recursive=True)
    observer.start()
    observer.join()

# Inicia o observador em uma thread separada
threading.Thread(target=start_observer, daemon=True).start()

if __name__ == "__main__":
    # Inicia o servidor com suporte a SocketIO
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)

