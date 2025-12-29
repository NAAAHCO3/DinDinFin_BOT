# app.py
from telegram.ext import Application
from config import BOT_TOKEN, SHEET_NAME, ABAS
from repositories.sheets_repository import SheetsRepository

# Importações explícitas evitam o NameError no ambiente de container
from services.transaction_service import TransactionService
from services.category_service import CategoryService
from services.account_service import AccountService
from services.budget_service import BudgetService
from services.ml_service import MLService
from services.export_service import ExportService

# Variáveis globais para os serviços
repo = None
transaction_service = None
category_service = None
account_service = None
budget_service = None
ml_service = None
export_service = None
app = None

def inicializar_bot():
    global repo, transaction_service, category_service, account_service
    global budget_service, ml_service, export_service, app
    
    if app is None:
        repo = SheetsRepository(SHEET_NAME)
        transaction_service = TransactionService(repo, ABAS)
        category_service = CategoryService(repo, ABAS)
        account_service = AccountService(repo, ABAS)
        budget_service = BudgetService(repo, ABAS)
        ml_service = MLService()
        export_service = ExportService()
        
        app = Application.builder().token(BOT_TOKEN).build()
        # Nota: Lembre-se de registrar seus handlers aqui no futuro
    return app

def telegram_webhook(request):
    from telegram import Update
    import asyncio
    
    # Garante que o bot está inicializado antes de processar
    application = inicializar_bot()
    
    update = Update.de_json(request.get_json(force=True), application.bot)
    asyncio.run(application.initialize())
    asyncio.run(application.process_update(update))
    return "OK", 200