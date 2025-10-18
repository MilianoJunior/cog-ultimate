import os
from flask import Flask
from flask_socketio import SocketIO

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'change-me')

# Se você NÃO instalar eventlet no ambiente local, o async_mode "threading" evita erros.
# Em produção (gunicorn -k eventlet), basta NÃO fixar "eventlet" aqui; o worker do gunicorn cuida disso.
ASYNC_MODE = os.getenv("ASYNC_MODE", "threading")  # 'threading' (dev) | 'eventlet' (opcional)

socketio = SocketIO(app, cors_allowed_origins="*", async_mode=ASYNC_MODE)

# importe suas rotas depois de criar app/socketio
from routes.routes import *  # noqa

if __name__ == "__main__":
    print("Iniciando servidor...")
    # Em dev, rode python main.py (Werkzeug) — sem Nginx
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)

# from flask import Flask
# # from livereload import Server
# import os
# from flask_socketio import SocketIO
# # from watchdog.observers import Observer
# # from watchdog.events import FileSystemEventHandler
# # import threading
# # from models.load_data import verify_all_connections

# app = Flask(__name__)
# # app.config['SECRET_KEY'] = 'secret!'
# app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'change-me')

# # Importa as rotas depois de criar a aplicação
# from routes.routes import *

# # Inicializa o SocketIO
# socketio = SocketIO(app, cors_allowed_origins="*")

# # Exemplo de evento para atualizar o cliente
# # @socketio.on('connect')
# # def handle_connect():
# #     pass

# # # Classe para lidar com eventos de mudança de arquivo
# # class ChangeHandler(FileSystemEventHandler):
# #     def on_modified(self, event):
# #         if event.src_path.endswith('.css') or event.src_path.endswith('.html'):
# #             socketio.emit('atualizar', {'arquivo': event.src_path})

# # Função para iniciar o observador
# # def start_observer():
# #     event_handler = ChangeHandler()
# #     observer = Observer()
# #     observer.schedule(event_handler, path='.', recursive=True)
# #     observer.start()
# #     observer.join()



# # Inicia o observador em uma thread separada
# # threading.Thread(target=start_observer, daemon=True).start()

# if __name__ == "__main__":
#     try:
#         print('Iniciando servidor...')
#         # Inicia o servidor com suporte a SocketIO
#         socketio.run(app, host='0.0.0.0', port=5000, debug=True)
#     except KeyboardInterrupt:
#         print('Servidor encerrado pelo usuário')
#     except Exception as e:
#         print('Erro ao iniciar servidor: ', e)
#     finally:
#         print('Servidor encerrado')
#         # verify_all_connections()


