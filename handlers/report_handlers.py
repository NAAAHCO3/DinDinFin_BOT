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
            f
