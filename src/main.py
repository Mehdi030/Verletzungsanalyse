import os
import sys
import logging
import colorlog
from flask import Flask, send_from_directory, request
from flask_cors import CORS
from src.routes.analysis import analysis_bp
from colorama import Fore, Style, init
init()

# Logging konfigurieren
handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter(
    "%(log_color)s%(asctime)s - %(levelname)s - %(message)s",
    datefmt=None,
    log_colors={
        'DEBUG':    'cyan',
        'INFO':     'green',
        'WARNING':  'yellow',
        'ERROR':    'red',
        'CRITICAL': 'bold_red',
    }
))

logger = colorlog.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(handler)

logging.getLogger('werkzeug').setLevel(logging.INFO)



# Flask-Anwendung erstellen
def create_app():
    app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
    app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

    # CORS aktivieren
    CORS(app)

    # Blueprint registrieren
    app.register_blueprint(analysis_bp, url_prefix='/api/analysis')

    # Statische Datei ausliefern
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve(path):
        static_folder_path = app.static_folder
        if static_folder_path is None:
            return "Static folder not configured", 404

        if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
            return send_from_directory(static_folder_path, path)
        else:
            index_path = os.path.join(static_folder_path, 'index.html')
            if os.path.exists(index_path):
                return send_from_directory(static_folder_path, 'index.html')
            else:
                return "index.html not found", 404

    # Eigene HTTP-Logausgabe
    @app.after_request
    def log_request(response):
        method = request.method
        path = request.path
        status = response.status_code

        color = {
            200: Fore.GREEN,
            201: Fore.CYAN,
            400: Fore.YELLOW,
            401: Fore.YELLOW,
            403: Fore.YELLOW,
            404: Fore.RED,
            500: Fore.RED
        }.get(status, Fore.WHITE)

        print(f"{color}{method} {path} → {status}{Style.RESET_ALL}")
        return response

    return app


# Server starten
def run_server(host='0.0.0.0', port=5000, debug=True):
    logger.info(f"Starte Server auf {host}:{port}...")

    app = create_app()
    app.run(host=host, port=port, debug=debug, use_reloader=False)


if __name__ == '__main__':
    run_server()

