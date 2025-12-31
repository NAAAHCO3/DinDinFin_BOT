import os

token = os.getenv("BOT_TOKEN")

print("TOKEN REPR:", repr(token))


import logging
from flask import Flask, request
from telegram import Update
from app import setup_application
import asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DinDinFin")

app = Flask(__name__)
bot_app = setup_application()

@app.route("/", methods=["GET"])
def health():
    return "OK", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json(force=True)
        update = Update.de_json(data, bot_app.bot)

        async def process():
            await bot_app.initialize()
            await bot_app.process_update(update)

        asyncio.run(process())
        return "OK", 200

    except Exception as e:
        logger.exception("Erro no webhook")
        return "Error", 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
