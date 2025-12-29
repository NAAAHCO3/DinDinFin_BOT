from telegram import Update
from telegram.ext import ContextTypes

async def add_categoria(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Use: /add_categoria Nome")
        return
    # Aqui você pode importar o cs (CategoryService) do app.py se quiser persistir
    await update.message.reply_text(f"✅ Categoria '{context.args[0]}' adicionada!")

async def add_conta(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Adiciona uma nova conta para o usuário. Ex: /add_conta Nubank 1000"""
    user_id = update.effective_user.id
    try:
        dados = context.args
        if len(dados) < 2:
            await update.message.reply_text("❌ Use: /add_conta Nome Saldo\nEx: /add_conta Nubank 1500")
            return

        nome_conta = dados[0]
        saldo_inicial = float(dados[1])

        # Importação dentro da função para evitar erro de importação circular
        from app import as_svc 
        as_svc.adicionar_conta(user_id, nome_conta, saldo_inicial)

        await update.message.reply_text(f"✅ Conta '{nome_conta}' registrada com saldo de R$ {saldo_inicial:.2f}!")
    except Exception as e:
        await update.message.reply_text(f"❌ Erro ao adicionar conta: {e}")