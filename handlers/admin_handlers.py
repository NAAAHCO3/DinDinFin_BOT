# handlers/admin_handlers.py

async def add_conta(update, context):
    """Adiciona uma nova conta para o usuário. Ex: /add_conta Nubank 1000"""
    user_id = update.effective_user.id
    try:
        # Espera algo como ['Nubank', '1000']
        dados = context.args
        if len(dados) < 2:
            await update.message.reply_text("❌ Use: /add_conta NomeDaConta SaldoInicial\nEx: /add_conta Nubank 1500")
            return

        nome_conta = dados[0]
        saldo_inicial = float(dados[1])

        from core.container import as_svc, cs
        as_svc.adicionar_conta(user_id, nome_conta, saldo_inicial)

        await update.message.reply_text(f"✅ Conta '{nome_conta}' registrada com saldo de R$ {saldo_inicial:.2f}!")
    except Exception as e:
        await update.message.reply_text(f"❌ Erro ao adicionar conta: {e}")