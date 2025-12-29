# handlers/report_handlers.py

async def resumo(update, context):
    """Gera um resumo simples dos gastos e rendas."""
    user_id = update.effective_user.id
    try:
        from app import ts # Importação local do transaction_service
        df = ts.df_usuario(user_id)
        
        if df.empty:
            await update.message.reply_text("📊 Você ainda não possui transações registradas.")
            return

        total_gastos = df[df['tipo'] == 'gasto']['valor'].sum()
        total_renda = df[df['tipo'] == 'renda']['valor'].sum()
        saldo = total_renda - total_gastos

        mensagem = (
            "📊 *Resumo Financeiro Geral*\n\n"
            f"💰 Renda Total: R$ {total_renda:.2f}\n"
            f"💸 Gastos Totais: R$ {total_gastos:.2f}\n"
            "----------------------------\n"
            f"💵 *Saldo Atual: R$ {saldo:.2f}*"
        )
        await update.message.reply_text(mensagem, parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text(f"❌ Erro ao gerar resumo: {e}")