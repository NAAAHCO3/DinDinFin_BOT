from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    CallbackQueryHandler,
    CommandHandler,
    filters
)

from core.container import (
    transaction_service,
    category_service,
    account_service,
    budget_service
)

# ================================
# Estados da Conversa
# ================================
VALOR, CATEGORIA, CONTA, DESCRICAO = range(4)


# ================================
# HELPERS
# ================================
def _teclado_opcoes(lista):
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton(item, callback_data=item)] for item in lista]
    )


async def _encerrar(update: Update, texto: str):
    if update.message:
        await update.message.reply_text(texto, parse_mode="Markdown")
    elif update.callback_query:
        await update.callback_query.edit_message_text(texto, parse_mode="Markdown")


# ================================
# ENTRADAS
# ================================
async def iniciar_gasto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.user_data["tipo"] = "gasto"
    await update.message.reply_text(
        "💸 *Registro de Gasto*\n\nInforme o valor:",
        parse_mode="Markdown"
    )
    return VALOR


async def iniciar_renda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.user_data["tipo"] = "renda"
    await update.message.reply_text(
        "💰 *Registro de Renda*\n\nInforme o valor:",
        parse_mode="Markdown"
    )
    return VALOR


# ================================
# VALOR
# ================================
async def receber_valor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        valor = float(update.message.text.replace(".", "").replace(",", "."))
        if valor <= 0:
            raise ValueError
        context.user_data["valor"] = valor
    except ValueError:
        await update.message.reply_text(
            "❌ Valor inválido.\nDigite um número maior que zero (ex: 50,00)."
        )
        return VALOR

    user_id = update.effective_user.id
    tipo = context.user_data["tipo"]

    categorias = category_service.listar_por_tipo(user_id, tipo)

    if not categorias:
        await _encerrar(
            update,
            f"⚠️ Você não possui categorias de *{tipo}*.\n"
            f"Use `/add_categoria Nome {tipo}`"
        )
        return ConversationHandler.END

    await update.message.reply_text(
        "📂 Selecione a categoria:",
        reply_markup=_teclado_opcoes(categorias)
    )
    return CATEGORIA


# ================================
# CATEGORIA
# ================================
async def receber_categoria(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    context.user_data["categoria"] = query.data
    user_id = update.effective_user.id

    contas = account_service.listar(user_id)

    if not contas:
        await _encerrar(
            update,
            "⚠️ Nenhuma conta encontrada.\n"
            "Use `/add_conta Banco 1000`"
        )
        return ConversationHandler.END

    await query.edit_message_text(
        "💳 Escolha a conta:",
        reply_markup=_teclado_opcoes(contas)
    )
    return CONTA


# ================================
# CONTA
# ================================
async def receber_conta(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    context.user_data["conta"] = query.data

    await query.edit_message_text(
        "📝 Digite uma descrição ou envie `nenhuma`:",
        parse_mode="Markdown"
    )
    return DESCRICAO


# ================================
# DESCRIÇÃO + PERSISTÊNCIA
# ================================
async def receber_descricao(update: Update, context: ContextTypes.DEFAULT_TYPE):
    descricao = update.message.text.strip()
    if descricao.lower() == "nenhuma":
        descricao = ""

    user_id = update.effective_user.id

    try:
        transaction_service.registrar(
            user_id=user_id,
            tipo=context.user_data["tipo"],
            valor=context.user_data["valor"],
            categoria=context.user_data["categoria"],
            conta=context.user_data["conta"],
            descricao=descricao
        )

        df = transaction_service.df_usuario(user_id)
        gastos = df[df["tipo"] == "gasto"]
        alertas = budget_service.alertas(user_id, gastos)

    except Exception:
        await update.message.reply_text(
            "❌ Erro ao registrar transação.\nTente novamente."
        )
        return ConversationHandler.END

    msg = "✅ *Transação registrada com sucesso!*"

    if alertas:
        msg += "\n\n⚠️ *Orçamento estourado:*"
        msg += "".join(f"\n• {c}" for c in alertas)

    await update.message.reply_text(msg, parse_mode="Markdown")
    return ConversationHandler.END


# ================================
# CANCELAMENTO
# ================================
async def cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await _encerrar(update, "❌ Operação cancelada.")
    return ConversationHandler.END


# ================================
# CONVERSATION HANDLER
# ================================
transaction_conversation = ConversationHandler(
    entry_points=[
        CommandHandler("gasto", iniciar_gasto),
        CommandHandler("renda", iniciar_renda),
    ],
    states={
        VALOR: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_valor)],
        CATEGORIA: [CallbackQueryHandler(receber_categoria)],
        CONTA: [CallbackQueryHandler(receber_conta)],
        DESCRICAO: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_descricao)],
    },
    fallbacks=[
        CommandHandler("cancel", cancelar)
    ],
    allow_reentry=True
)
