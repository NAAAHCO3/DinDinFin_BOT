import os
import logging
from threading import Thread
from flask import Flask
from app import start_bot

# Configuração de logs para vermos o que acontece no GCP
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route("/")
def health_check():
    return "OK", 200

def run_telegram_thread():
    try:
        logger.info("Iniciando thread do Telegram...")
        start_bot()
    except Exception as e:
        logger.error(f"Erro na thread do bot: {e}")

if __name__ == "__main__":
    # 1. Prepara a thread do bot mas não espera ela travar o processo
    bot_thread = Thread(target=run_telegram_thread, daemon=True)
    bot_thread.start()
    
    # 2. Inicia o Flask na porta correta (isso deve ser imediato)
    port = int(os.environ.get("PORT", 8080))
    logger.info(f"Servidor Flask ouvindo na porta {port}")
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)