# main.py
import os
from threading import Thread
from flask import Flask
from app import inicializar_bot_polling

app = Flask(__name__)

@app.route("/")
def health_check():
    return "Bot is running!", 200

def run_telegram():
    # Esta função roda o bot em modo polling infinito
    inicializar_bot_polling()

if __name__ == "__main__":
    # Inicia o bot em uma Thread separada
    Thread(target=run_telegram).start()
    
    # Inicia o Flask na porta que o Google exige
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)