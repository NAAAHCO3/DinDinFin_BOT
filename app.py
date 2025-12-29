# app.py
from telegram.ext import Application
from config import BOT_TOKEN, SHEET_NAME, ABAS
from repositories.sheets_repository import SheetsRepository
from services import *

repo = SheetsRepository(SHEET_NAME)

transaction_service = TransactionService(repo, ABAS)
category_service = CategoryService(repo, ABAS)
account_service = AccountService(repo, ABAS)
budget_service = BudgetService(repo, ABAS)
ml_service = MLService()
export_service = ExportService()

app = Application.builder().token(BOT_TOKEN).build()

def telegram_webhook(request):
    from telegram import Update
    import asyncio
    update = Update.de_json(request.get_json(force=True), app.bot)
    asyncio.run(app.initialize())
    asyncio.run(app.process_update(update))
    return "OK", 200
