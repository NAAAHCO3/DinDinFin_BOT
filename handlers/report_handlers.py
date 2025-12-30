# handlers/report_handlers.py

from telegram import Update
from telegram.ext import ContextTypes

from core.container import ts


# =========================
# RESUMO FINANCEIRO
# =========================
async def resumo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gera um resumo financeiro geral do usuário."""

    user_id = update.effective_user.id

    try:
        df = ts.df_usuario(user_id)

        if df is None or df.empty:
            await _responder(
                update,
                "🔎 *Nenhuma transação encontrada.*\n"
                "Registre gastos ou rendas para visualizar o resumo.",
            )
            return

        # Validação defensiva
        colunas_necessarias = {"tipo", "valor"}
        if not colunas_necessarias.issubset(df.columns):
            raise ValueError("Estrutura de dados inválida")

        total_gastos = df.loc[df["tipo"] == "gasto", "valor"].sum()
        total_renda = df.loc[df["tipo"] == "renda", "valor"].sum()
        saldo = total_renda - total_gastos

        mensagem = (
            "📊 *Resumo Financeiro Geral*\n\n"
            f"💰 *Renda Total:* R$ {total_renda:,.2f}\n"
            f"📉 *Gastos Totais:* R$ {total_gastos:,.2f}\n"
            "────────────────────\n"
            f"🏁 *Saldo Atual:* R$ {saldo:,.2f}"
        )

        await _responder(update, mensagem)

    except Exception as e:
        # Ideal: logar o erro (logger.error)
        await _responder(
            update,
            "❌ *Não foi possível gerar o resumo agora.*\n"
            "Tente novamente em instantes."
        )


# =========================
# UTILITÁRIO DE RESPOSTA
# =========================
async def _responder(update: Update, texto: str):
    """Responde corretamente tanto para mensagem quanto callback."""
    if update.message:
        await update.message.reply_text(texto, parse_mode="Markdown")
    elif update.callback_query:
        await update.callback_query.edit_message_text(
            texto,
            parse_mode="Markdown"
        )
