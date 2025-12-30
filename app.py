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
        "Utilize o menu abaixo para gerenciar suas finanças de forma rápida:"
    )
    
    await update.message.reply_text(
        texto_boas_vindas, 
        reply_markup=reply_markup, 
        parse_mode='Markdown'
    )

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
# BOOTSTRAP DO BOT
# ============================
def start_bot():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN não definido")

    logger.info("Iniciando Telegram Bot...")

    application = Application.builder().token(BOT_TOKEN).build()

    # Menu Principal
    application.add_handler(CommandHandler("start", start))
    
    # Handler para capturar cliques nos botões do Menu Principal
    application.add_handler(CallbackQueryHandler(processar_botoes_menu, pattern="^menu_"))

    # Fluxo de Conversação (Gasto/Renda)
    application.add_handler(transaction_conversation)

    # Comandos Administrativos
    application.add_handler(CommandHandler("add_categoria", add_categoria))
    application.add_handler(CommandHandler("add_conta", add_conta))

    # Comando direto de Resumo
    application.add_handler(CommandHandler("resumo", resumo))

    logger.info("Bot iniciado e aguardando interações.")
    application.run_polling(stop_signals=None)

if __name__ == "__main__":
    try:
        start_bot()
    except Exception:
        logger.exception("Falha crítica ao iniciar o bot")