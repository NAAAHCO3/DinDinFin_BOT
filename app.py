import asyncio
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

# Importações dos Handlers (Comandos)
from handlers.transaction_handlers import transaction_conversation
from handlers.admin_handlers import add_categoria, add_conta
from handlers.report_handlers import resumo # Certifique-se de que o nome da função está correto no seu arquivo

# Variáveis globais para manter a instância em cache (Singleton)
app_instance = None

def inicializar_bot():
    global app_instance
    
    if app_instance is None:
        # 1. Inicia Repositório e Serviços
        repo = SheetsRepository(SHEET_NAME)
        ts = TransactionService(repo, ABAS)
        cs = CategoryService(repo, ABAS)
        as_svc = AccountService(repo, ABAS)
        bs = BudgetService(repo, ABAS)
        mls = MLService()
        es = ExportService()
        
        # 2. Constrói a Aplicação
        builder = Application.builder().token(BOT_TOKEN)
        application = builder.build()
        
        # 3. REGISTRA OS COMANDOS (O que estava faltando!)
        # Comando Start simples
        application.add_handler(CommandHandler("start", lambda u, c: u.message.reply_text("💰 DinDinFinBot Ativo!\nUse /gasto ou /renda para começar.")))
        
        # Handlers complexos (Conversação)
        application.add_handler(transaction_conversation) 
        
        # Comandos de Admin/Config
        application.add_handler(CommandHandler("add_categoria", add_categoria))
        application.add_handler(CommandHandler("add_conta", add_conta))
        application.add_handler(CommandHandler("resumo", resumo))
        
        app_instance = application
        
    return app_instance

def telegram_webhook(request):
    """Ponto de entrada chamado pelo Google Cloud Run"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    application = inicializar_bot()
    
    # Processa a atualização vinda do Telegram
    payload = request.get_json(force=True)
    update = Update.de_json(payload, application.bot)
    
    loop.run_until_complete(application.initialize())
    loop.run_until_complete(application.process_update(update))
    
    return "OK", 200