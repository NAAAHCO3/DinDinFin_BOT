# Em main.py
import os
import asyncio
from flask import Flask, request
from app import setup_bot
from telegram import Update

app = Flask(__name__)
bot_app = None

@app.before_first_request
def init_bot():
    global bot_app
    bot_app = asyncio.run(setup_bot())

@app.route("/", methods=["POST"])
def webhook():
    if bot_app:
        update = Update.de_json(request.get_json(force=True), bot_app.bot)
        asyncio.run(bot_app.process_update(update))
    return "OK", 200

@app.route("/health", methods=["GET"])
def health():
    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)