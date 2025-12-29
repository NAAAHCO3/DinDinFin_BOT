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

        # Chamamos o serviço de conta (que já existe no seu projeto)
        # Nota: O bot_manager ou inicializar_bot deve fornecer a instância do serviço
        from app import as_svc # Importação local para evitar erro circular
        as_svc.adicionar_conta(user_id, nome_conta, saldo_inicial)

        await update.message.reply_text(f"✅ Conta '{nome_conta}' registrada com saldo de R$ {saldo_inicial:.2f}!")
    except Exception as e:
        await update.message.reply_text(f"❌ Erro ao adicionar conta: {e}")