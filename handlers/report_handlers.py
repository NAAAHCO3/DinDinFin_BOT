# handlers/report_handlers.py
async def resumo(update, context):
    df = transaction_service.df_usuario(update.effective_user.id)

    renda = df[df.tipo == "renda"]["valor"].sum()
    gasto = df[df.tipo == "gasto"]["valor"].sum()

    await update.message.reply_text(
        f"📊 Resumo\n\n💵 {renda:.2f}\n💸 {gasto:.2f}\n💰 {renda-gasto:.2f}"
    )
