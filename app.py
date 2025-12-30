import logging
import sys

from telegram.ext import Application, CommandHandler

from config import BOT_TOKEN
from core.container import (
    transaction_service,
    category_service,
    account_service,
)
from handlers.transaction_handlers import transaction_conversation
from handlers.admin_handlers import add_categoria, add_conta
from handlers.report_handlers import resumo


# ============================
# LOGGING GLOBAL
# ============================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    stream=sys.stdout,
)

logger = logging.getLogger(__name__)


# ============================
# HANDLERS SIMPLES
# ============================
async def start(update, context):
    await update.message.reply_text("🤖 Bot Online e funcionando!")


# ============================
# BOOTSTRAP DO BOT
# ============================
def start_bot():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN não definido")

    logger.info("Iniciando Telegram Bot...")

    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .build()
    )

    # Comandos básicos
    application.add_handler(CommandHandler("start", start))

    # Conversações
    application.add_handler(transaction_conversation)

    # Administração
    application.add_handler(CommandHandler("add_categoria", add_categoria))
    application.add_handler(CommandHandler("add_conta", add_conta))

    # Relatórios
    application.add_handler(CommandHandler("resumo", resumo))

    logger.info("Bot iniciado. Aguardando mensagens...")

    # stop_signals=None é ESSENCIAL para Cloud Run / Docker
    application.run_polling(stop_signals=None)


# ============================
# ENTRYPOINT
# ============================
if __name__ == "__main__":
    try:
        start_bot()
    except Exception:
        logger.exception("Falha crítica ao iniciar o bot")
        raise
