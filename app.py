import logging
import sys
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

from config import BOT_TOKEN
from handlers.transaction_handlers import (
    transaction_conversation, 
    iniciar_gasto, 
    iniciar_renda
)
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
# MENU PRINCIPAL (UX PROFISSIONAL)
# ============================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Exibe o Painel de Controle principal com botões."""
    keyboard = [
        [
            InlineKeyboardButton("💸 Registrar Gasto", callback_data="menu_gasto"),
            InlineKeyboardButton("💰 Registrar Renda", callback_data="menu_renda")
        ],
        [
            InlineKeyboardButton("📊 Ver Resumo", callback_data="menu_resumo"),
            InlineKeyboardButton("⚙️ Configurações", callback_data="menu_config")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    texto_boas_vindas = (
        "🚀 *DinDinFin PRO*\n"
        "Seu assistente financeiro inteligente.\n\n"
        "Utilize o menu abaixo para gerenciar suas finanças:"
    )
    
    # No Webhook, o update pode vir de uma mensagem ou de um clique em botão (callback)
    if update.message:
        await update.message.reply_text(texto_boas_vindas, reply_markup=reply_markup, parse_mode='Markdown')
    elif update.callback_query:
        await update.callback_query.message.reply_text(texto_boas_vindas, reply_markup=reply_markup, parse_mode='Markdown')

async def processar_botoes_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gerencia os cliques nos botões do menu principal."""
    query = update.callback_query
    await query.answer()

    if query.data == "menu_gasto":
        return await iniciar_gasto(update, context)
    elif query.data == "menu_renda":
        return await iniciar_renda(update, context)
    elif query.data == "menu_resumo":
        return await resumo(update, context)
    elif query.data == "menu_config":
        await query.message.reply_text("⚙️ *Configurações:*\nUse /add_categoria ou /add_conta", parse_mode='Markdown')

# ============================
# CONFIGURAÇÃO DO BOT (PARA WEBHOOK)
# ============================
def setup_application():
    """Configura e retorna a aplicação sem iniciar o polling."""
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN não definido")

    # Inicializa a aplicação configurada para receber updates via Webhook
    application = Application.builder().token(BOT_TOKEN).updater(None).build()

    # Registro de Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(processar_botoes_menu, pattern="^menu_"))
    application.add_handler(transaction_conversation)
    application.add_handler(CommandHandler("add_categoria", add_categoria))
    application.add_handler(CommandHandler("add_conta", add_conta))
    application.add_handler(CommandHandler("resumo", resumo))

    return application