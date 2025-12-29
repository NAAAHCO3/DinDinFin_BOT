# config.py
import os

BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
SHEET_NAME = os.getenv("GOOGLE_SHEET_NAME", "DinDinFinBOT")

ABAS = {
    "TRANSACOES": "Transacoes",
    "CATEGORIAS": "Categorias",
    "CONTAS": "Contas",
    "ORCAMENTOS": "Orcamentos"
}
