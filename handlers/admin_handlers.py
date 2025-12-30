from telegram import Update
from telegram.ext import ContextTypes
from core.container import as_svc, cs # Importa os serviços do container

async def add_categoria(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Adiciona categoria real na planilha"""
    user_id = update.effective_user.id
    if not context.args:
        await update.message.reply_text("❌ Use: /add_categoria Nome")
        return
    
    nome_cat = " ".join(context.args)
    try:
        cs.adicionar(user_id, nome_cat) # Chama o método correto do category_service
        await update.message.reply_text(f"✅ Categoria '{nome_cat}' adicionada!")
    except Exception as e:
        await update.message.reply_text(f"❌ Erro: {e}")

async def add_conta(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Adiciona conta real na planilha"""
    user_id = update.effective_user.id
    try:
        if len(context.args) < 2:
            await update.message.reply_text("❌ Use: /add_conta Nome Saldo")
            return

        nome_conta = context.args[0]
        saldo = float(context.args[1].replace(",", "."))

        # CORREÇÃO AQUI: Mudado de adicionar_conta para criar
        as_svc.criar(user_id, nome_conta, saldo)

        await update.message.reply_text(f"✅ Conta '{nome_conta}' registrada!")
    except Exception as e:
        await update.message.reply_text(f"❌ Erro ao adicionar conta: {e}")