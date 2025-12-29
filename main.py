import os
import asyncio
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

def run_bot_in_thread():
    """Cria um novo loop de eventos para a thread do bot"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        logger.info("Iniciando bot do Telegram...")
        start_bot()
    except Exception as e:
        logger.error(f"Erro crítico no bot: {e}")

if __name__ == "__main__":
    # 1. Inicia o bot em uma thread separada com loop próprio
    bot_thread = Thread(target=run_bot_in_thread, daemon=True)
    bot_thread.start()
    
    # 2. Inicia o Flask (Obrigatório para o Cloud Run)
    port = int(os.environ.get("PORT", 8080))
    logger.info(f"Servidor Flask ouvindo na porta {port}")
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)