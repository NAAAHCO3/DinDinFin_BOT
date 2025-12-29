import asyncio
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler
from config import BOT_TOKEN, SHEET_NAME, ABAS
from repositories.sheets_repository import SheetsRepository

# Importações dos Serviços
from services.transaction_service import TransactionService
from services.category_service import CategoryService
from services.account_service import AccountService
from services.budget_service import BudgetService
from services.ml_service import MLService
from services.export_service import ExportService

# 1. INSTÂNCIAS GLOBAIS (Criadas fora da classe para os handlers importarem)
repo = SheetsRepository(SHEET_NAME)
ts = TransactionService(repo, ABAS)
cs = CategoryService(repo, ABAS)
as_svc = AccountService(repo, ABAS)
bs = BudgetService(repo, ABAS)
mls = MLService()
es = ExportService()

# 2. IMPORTAÇÃO DOS HANDLERS (Abaixo dos serviços!)
from handlers.transaction_handlers import transaction_conversation
from handlers.admin_handlers import add_categoria, add_conta
from handlers.report_handlers import resumo

class DinDinBotApp:
    def build(self):
        # Configura o Bot
        self.application = Application.builder().token(BOT_TOKEN).build()

        # Registra os Comandos
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(transaction_conversation) 
        self.application.add_handler(CommandHandler("add_categoria", add_categoria))
        self.application.add_handler(CommandHandler("add_conta", add_conta))
        self.application.add_handler(CommandHandler("resumo", resumo))
        
        return self.application

    async def start_command(self, update: Update, context):
        await update.message.reply_text("💰 DinDinFinBot Online!\nUse /gasto ou /add_conta para começar.")

def start_bot():
    """Chamado pela Thread no main.py"""
    try:
        app_builder = DinDinBotApp()
        application = app_builder.build()
        application.run_polling()
    except Exception as e:
        logging.error(f"Erro no Bot: {e}")