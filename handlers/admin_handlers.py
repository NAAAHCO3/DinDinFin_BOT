# handlers/admin_handlers.py
async def add_categoria(update, context):
    categoria = " ".join(context.args)
    category_service.adicionar(update.effective_user.id, categoria)
    await update.message.reply_text("Categoria adicionada.")
