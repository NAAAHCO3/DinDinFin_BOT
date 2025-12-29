import os
import logging
from threading import Thread
from flask import Flask
from app import start_bot

# Configuração de logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route("/")
def health_check():
    return "OK", 200

def run_flask():
    """Roda o Flask em uma thread secundária"""
    port = int(os.environ.get("PORT", 8080))
    logger.info(f"Servidor Flask iniciando na porta {port}")
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)

if __name__ == "__main__":
    # 1. Inicia o Flask em segundo plano
    flask_thread = Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    # 2. Inicia o bot na THREAD PRINCIPAL (Resolve o erro set_wakeup_fd)
    try:
        logger.info("Iniciando bot do Telegram na thread principal...")
        start_bot()
    except Exception as e:
        logger.error(f"Erro crítico no bot: {e}")