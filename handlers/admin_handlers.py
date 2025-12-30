from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import ContextTypes

from core.container import as_svc, cs


# =========================
# MENU PRINCIPAL
# =========================
async def menu_principal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Exibe o painel principal do bot"""

    teclado = [
        [
            InlineKeyboardButton("💸 Registrar Gasto", callback_data="fluxo_gasto"),
            InlineKeyboardButton("💰 Registrar Renda", callback_data="fluxo_renda"),
        ],
        [
            InlineKeyboardButton("📊 Relatórios", callback_data="menu_relatorios"),
            InlineKeyboardButton("⚙️ Configurações", callback_data="menu_config"),
        ]
    ]

    reply_markup = InlineKeyboardMarkup(teclado)

    texto = (
        "🏦 *DinDinFin — Painel de Controle*\n\n"
        "Escolha uma das opções abaixo para continuar:"
    )

    if update.message:
        await update.message.reply_text(
            texto,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    elif update.callback_query:
        await update.callback_query.edit_message_text(
            texto,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )


# =========================
# CATEGORIAS
# =========================
async def add_categoria(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Adiciona uma nova categoria de renda ou gasto.
    Uso:
        /add_categoria Nome renda|gasto
    """
    user_id = update.effective_user.id

    if len(context.args) < 2:
        await update.message.reply_text(
            "❗ *Uso correto:*\n"
            "`/add_categoria Nome renda|gasto`\n\n"
            "Exemplo:\n"
            "`/add_categoria Salário renda`",
            parse_mode="Markdown"
        )
        return

    nome = context.args[0]
    tipo = context.args[1].lower()

    if tipo not in {"renda", "gasto"}:
        await update.message.reply_text(
            "❌ Tipo inválido.\nUse apenas: `renda` ou `gasto`",
            parse_mode="Markdown"
        )
        return

    try:
        cs.adicionar(user_id, nome, tipo)
        await update.message.reply_text(
            f"✅ Categoria *{nome}* ({tipo}) adicionada com sucesso!",
            parse_mode="Markdown"
        )
    except Exception as e:
        await update.message.reply_text(
            f"❌ Erro ao adicionar categoria:\n`{e}`",
            parse_mode="Markdown"
        )


# =========================
# CONTAS
# =========================
async def add_conta(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Adiciona uma conta financeira.
    Uso:
        /add_conta Nome Saldo
    """
    user_id = update.effective_user.id

    if len(context.args) < 2:
        await update.message.reply_text(
            "❗ *Uso correto:*\n"
            "`/add_conta Nome_do_Banco Saldo`\n\n"
            "Exemplo:\n"
            "`/add_conta Nubank 1500.50`",
            parse_mode="Markdown"
        )
        return

    nome_conta = context.args[0]

    try:
        saldo = float(context.args[1].replace(",", "."))
    except ValueError:
        await update.message.reply_text(
            "❌ Saldo inválido. Use apenas números.\n"
            "Ex: `1000` ou `1500.75`",
            parse_mode="Markdown"
        )
        return

    try:
        as_svc.criar(user_id, nome_conta, saldo)
        await update.message.reply_text(
            f"✅ Conta *{nome_conta}* criada com saldo inicial de *R$ {saldo:.2f}*",
            parse_mode="Markdown"
        )
    except Exception as e:
        await update.message.reply_text(
            f"❌ Erro ao criar conta:\n`{e}`",
            parse_mode="Markdown"
        )
