import os
import logging
from threading import Thread
from flask import Flask
from app import start_bot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route("/")
def health_check():
    return "OK", 200

def run_flask():
    """Roda o Flask em segundo plano para o GCP validar o deploy"""
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)

if __name__ == "__main__":
    # 1. Inicia o Flask em uma thread separada
    Thread(target=run_flask, daemon=True).start()
    
    # 2. Inicia o bot na thread principal (Obrigatório para evitar erros de sinal)
    try:
        logger.info("Iniciando bot na thread principal...")
        start_bot()
    except Exception as e:
        logger.error(f"Erro fatal no bot: {e}")