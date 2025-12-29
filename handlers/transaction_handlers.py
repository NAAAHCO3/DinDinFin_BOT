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

# ================================
# Estados da Conversa
# ================================
VALOR, CATEGORIA, CONTA, DESCRICAO = range(4)

# ================================
# Entradas
# ================================
async def iniciar_gasto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.user_data["tipo"] = "gasto"
    await update.message.reply_text("💸 Informe o valor do gasto:")
    return VALOR


async def iniciar_renda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.user_data["tipo"] = "renda"
    await update.message.reply_text("💵 Informe o valor da renda:")
    return VALOR


# ================================
# Valor
# ================================
async def receber_valor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        valor = float(update.message.text.replace(",", "."))
        if valor <= 0:
            raise ValueError
        context.user_data["valor"] = valor
    except ValueError:
        await update.message.reply_text("❌ Digite um valor numérico válido.")
        return VALOR

    categorias = category_service.listar(update.effective_user.id)

    if not categorias:
        await update.message.reply_text(
            "⚠️ Você ainda não cadastrou categorias.\n"
            "Use /add_categoria Alimentação"
        )
        return ConversationHandler.END

    teclado = [
        [InlineKeyboardButton(c, callback_data=c)]
        for c in categorias
    ]

    await update.message.reply_text(
        "📂 Escolha a categoria:",
        reply_markup=InlineKeyboardMarkup(teclado)
    )
    return CATEGORIA


# ================================
# Categoria
# ================================
async def receber_categoria(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    context.user_data["categoria"] = query.data

    contas = account_service.listar(update.effective_user.id)

    if not contas:
        await query.edit_message_text(
            "⚠️ Nenhuma conta cadastrada.\n"
            "Use /add_conta Banco 1000"
        )
        return ConversationHandler.END

    teclado = [
        [InlineKeyboardButton(c, callback_data=c)]
        for c in contas
    ]

    await query.edit_message_text(
        "🏦 Escolha a conta:",
        reply_markup=InlineKeyboardMarkup(teclado)
    )
    return CONTA


# ================================
# Conta
# ================================
async def receber_conta(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    context.user_data["conta"] = query.data

    await query.edit_message_text(
        "📝 Digite uma descrição (ou 'nenhuma'):"
    )
    return DESCRICAO


# ================================
# Descrição + Persistência
# ================================
async def receber_descricao(update: Update, context: ContextTypes.DEFAULT_TYPE):
    descricao = update.message.text
    if descricao.lower() == "nenhuma":
        descricao = ""

    user_id = update.effective_user.id

    transaction_service.registrar(
        user_id=user_id,
        tipo=context.user_data["tipo"],
        valor=context.user_data["valor"],
        categoria=context.user_data["categoria"],
        conta=context.user_data["conta"],
        descricao=descricao
    )

    # ================================
    # ALERTA DE ORÇAMENTO
    # ================================
    df = transaction_service.df_usuario(user_id)
    gastos = df[df["tipo"] == "gasto"]
    alertas = budget_service.alertas(user_id, gastos)

    msg = "✅ Transação registrada com sucesso!"

    if alertas:
        msg += "\n\n⚠️ *Alerta de orçamento estourado:*"
        for c in alertas:
            msg += f"\n• {c}"

    await update.message.reply_text(msg, parse_mode="Markdown")

    return ConversationHandler.END


# ================================
# Handler Unificado
# ================================
transaction_conversation = ConversationHandler(
    entry_points=[
        CommandHandler("gasto", iniciar_gasto),
        CommandHandler("renda", iniciar_renda)
    ],
    states={
        VALOR: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_valor)],
        CATEGORIA: [CallbackQueryHandler(receber_categoria)],
        CONTA: [CallbackQueryHandler(receber_conta)],
        DESCRICAO: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_descricao)],
    },
    fallbacks=[],
)
