# app.py
from telegram.ext import Application
from config import BOT_TOKEN, SHEET_NAME, ABAS
from repositories.sheets_repository import SheetsRepository

# Importações explícitas para evitar NameError
from services.transaction_service import TransactionService
from services.category_service import CategoryService
from services.account_service import AccountService
from services.budget_service import BudgetService
from services.ml_service import MLService
from services.export_service import ExportService

# Variáveis globais para instâncias
repo = None
app = None

def get_app():
    global repo, app
    if app is None:
        # Inicia o repositório e serviços apenas quando necessário
        repo = SheetsRepository(SHEET_NAME)
        # Injeção de dependências nos serviços
        transaction_service = TransactionService(repo, ABAS)
        category_service = CategoryService(repo, ABAS)
        account_service = AccountService(repo, ABAS)
        budget_service = BudgetService(repo, ABAS)
        
        app = Application.builder().token(BOT_TOKEN).build()
        # Aqui você deve adicionar os handlers ao app se necessário
    return app

def telegram_webhook(request):
    import asyncio
    from telegram import Update
    
    application = get_app()
    update = Update.de_json(request.get_json(force=True), application.bot)
    
    asyncio.run(application.initialize())
    asyncio.run(application.process_update(update))
    return "OK", 200