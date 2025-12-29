# app.py
import logging
from telegram.ext import Application, CommandHandler
from config import BOT_TOKEN
from core.container import ts, cs, as_svc # Apenas para garantir carga
from handlers.transaction_handlers import transaction_conversation
from handlers.admin_handlers import add_categoria, add_conta
from handlers.report_handlers import resumo

async def setup_bot():
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Registro de Handlers
    application.add_handler(CommandHandler("start", lambda u, c: u.message.reply_text("Bot Online!")))
    application.add_handler(transaction_conversation)
    application.add_handler(CommandHandler("add_categoria", add_categoria))
    application.add_handler(CommandHandler("add_conta", add_conta))
    application.add_handler(CommandHandler("resumo", resumo))
    
    await application.initialize()
    return application