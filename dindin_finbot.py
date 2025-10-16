# -*- coding: utf-8 -*-
import os
import gspread
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import io

from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters, ContextTypes,
    ConversationHandler, CallbackQueryHandler
)

# --- CONFIGURAÇÕES E CONSTANTES ---
TOKEN = os.getenv("TELEGRAM_TOKEN")
NOME_DA_PLANILHA = os.getenv("GOOGLE_SHEET_NAME", "DinDinFinBOT")

# Estados para o ConversationHandler
VALOR, CATEGORIA, DESCRICAO = range(3)
# Tipos de transação
GASTO, RENDA = "gasto", "renda"

# --- FUNÇÕES AUXILIARES DE ACESSO À PLANILHA ---

def get_sheet(sheet_name):
    """Acessa uma aba específica da planilha pelo nome."""
    try:
        gc = gspread.service_account(filename='credentials.json')
        spreadsheet = gc.open(NOME_DA_PLANILHA)
        return spreadsheet.worksheet(sheet_name)
    except gspread.exceptions.WorksheetNotFound:
        raise Exception(f"Aba '{sheet_name}' não encontrada na planilha. Por favor, crie-a.")
    except Exception as e:
        raise Exception(f"Erro ao conectar com o Google Sheets: {e}")

def get_categories(tipo):
    """Busca as categorias (gasto ou renda) da aba 'Configuracoes'."""
    sheet = get_sheet("Configuracoes")
    all_configs = sheet.get_all_records()
    df = pd.DataFrame(all_configs)
    return df[df['tipo'] == tipo]['nome'].tolist()

def add_category_to_sheet(tipo, nome):
    """Adiciona uma nova categoria na aba 'Configuracoes'."""
    sheet = get_sheet("Configuracoes")
    # Verifica se a categoria já existe
    if nome.lower() in [cat.lower() for cat in get_categories(tipo)]:
        return False
    sheet.append_row([tipo, nome])
    return True

def delete_category_from_sheet(tipo, nome):
    """Deleta uma categoria da aba 'Configuracoes'."""
    sheet = get_sheet("Configuracoes")
    cell = sheet.find(nome, in_column=2)
    if cell and sheet.cell(cell.row, 1).value == tipo:
        sheet.delete_rows(cell.row)
        return True
    return False

# --- COMANDOS PRINCIPAIS (/start, /ajuda) ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [["/gasto", "/renda"], ["/resumo", "/extrato"], ["/categorias", "/ajuda"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        'Olá! Bem-vindo ao seu Assistente Financeiro Ultimate!\n\n'
        'Use os botões para registrar transações, ver relatórios e gerenciar suas categorias.',
        reply_markup=reply_markup
    )

async def ajuda(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_text = (
        "🌟 **Guia de Comandos** 🌟\n\n"
        "**Transações:**\n"
        "/gasto - Inicia o registro guiado de uma despesa.\n"
        "/renda - Inicia o registro guiado de uma receita.\n\n"
        "**Relatórios:**\n"
        "/extrato - Mostra suas últimas 10 transações.\n"
        "/resumo [mm/aaaa] - Um resumo financeiro e gráfico do mês.\n\n"
        "**Gerenciamento:**\n"
        "/categorias - Lista todas as suas categorias.\n"
        "/addcategoria <tipo> <nome> - Adiciona uma nova categoria. Ex: `/addcategoria gasto streaming`\n"
        "/delcategoria <tipo> <nome> - Remove uma categoria. Ex: `/delcategoria renda bonus`\n"
        "/cancelar - Cancela o registro de uma transação a qualquer momento."
    )
    await update.message.reply_text(help_text, parse_mode='Markdown')

# --- CONVERSATION HANDLER PARA REGISTRO DE TRANSAÇÕES ---

async def iniciar_transacao(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Inicia o processo de registro (gasto ou renda)."""
    context.user_data['tipo'] = GASTO if update.message.text.startswith('/gasto') else RENDA
    await update.message.reply_text(f"Qual o valor da transação?")
    return VALOR

async def receber_valor(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Recebe o valor e pede a categoria."""
    try:
        valor = float(update.message.text.replace(',', '.'))
        if valor <= 0:
            await update.message.reply_text("O valor deve ser positivo. Por favor, insira novamente.")
            return VALOR
        context.user_data['valor'] = valor
    except ValueError:
        await update.message.reply_text("Valor inválido. Por favor, insira apenas números.")
        return VALOR

    tipo_transacao = context.user_data['tipo']
    categorias = get_categories(tipo_transacao)
    
    keyboard = [[InlineKeyboardButton(cat.capitalize(), callback_data=cat)] for cat in categorias]
    keyboard.append([InlineKeyboardButton("Outra (digitar)", callback_data='custom_category')])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(f"Selecione a categoria para este {tipo_transacao}:", reply_markup=reply_markup)
    return CATEGORIA

async def receber_categoria_botao(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Recebe a categoria via botão e pede a descrição."""
    query = update.callback_query
    await query.answer()
    categoria = query.data

    if categoria == 'custom_category':
        await query.edit_message_text(text="Ok, por favor, digite o nome da nova categoria.")
        return CATEGORIA
    else:
        context.user_data['categoria'] = categoria
        await query.edit_message_text(text=f"Categoria '{categoria.capitalize()}' selecionada.")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Agora, adicione uma descrição (ou digite /pular).")
        return DESCRICAO

async def receber_categoria_texto(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Recebe a categoria via texto (se 'Outra' foi selecionado)."""
    context.user_data['categoria'] = update.message.text.lower()
    await update.message.reply_text("Agora, adicione uma descrição (ou digite /pular).")
    return DESCRICAO

async def receber_descricao(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Recebe a descrição e finaliza a transação."""
    context.user_data['descricao'] = update.message.text
    return await finalizar_transacao(update, context)

async def pular_descricao(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Pula a etapa de descrição e finaliza."""
    context.user_data['descricao'] = ""
    return await finalizar_transacao(update, context)

async def finalizar_transacao(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Salva a transação na planilha e encerra a conversa."""
    try:
        sheet = get_sheet("Transacoes")
        dados = context.user_data
        nova_linha = [
            str(datetime.now().date()),
            dados['tipo'],
            dados['valor'],
            dados['categoria'],
            dados.get('descricao', ''),
            update.effective_user.id
        ]
        sheet.append_row(nova_linha)
        
        tipo_str = "Gasto" if dados['tipo'] == GASTO else "Renda"
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"✅ {tipo_str} de R${dados['valor']:.2f} em '{dados['categoria'].capitalize()}' registrado com sucesso!"
        )
    except Exception as e:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"❌ Erro ao salvar: {e}")
    
    context.user_data.clear()
    return ConversationHandler.END

async def cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancela o processo de registro."""
    await update.message.reply_text("Registro cancelado.")
    context.user_data.clear()
    return ConversationHandler.END

# --- COMANDOS DE GERENCIAMENTO DE CATEGORIAS ---

async def listar_categorias(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        gastos = get_categories(GASTO)
        rendas = get_categories(RENDA)
        
        texto = "📋 **Suas Categorias:**\n\n**Gastos:**\n"
        texto += " - " + "\n - ".join(sorted([g.capitalize() for g in gastos])) if gastos else "Nenhuma categoria de gasto."
        texto += "\n\n**Rendas:**\n"
        texto += " - " + "\n - ".join(sorted([r.capitalize() for r in rendas])) if rendas else "Nenhuma categoria de renda."

        await update.message.reply_text(texto, parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text(f"❌ Erro ao buscar categorias: {e}")

async def adicionar_categoria(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        if len(context.args) != 2:
            await update.message.reply_text("Formato incorreto. Use: `/addcategoria <tipo> <nome>`\nEx: `/addcategoria gasto streaming`")
            return
        
        tipo, nome = context.args[0].lower(), " ".join(context.args[1:]).lower()
        if tipo not in [GASTO, RENDA]:
            await update.message.reply_text(f"Tipo inválido. Use '{GASTO}' ou '{RENDA}'.")
            return

        if add_category_to_sheet(tipo, nome):
            await update.message.reply_text(f"✅ Categoria '{nome.capitalize()}' adicionada em '{tipo.capitalize()}'.")
        else:
            await update.message.reply_text(f"⚠️ Categoria '{nome.capitalize()}' já existe.")

    except Exception as e:
        await update.message.reply_text(f"❌ Erro ao adicionar categoria: {e}")

async def deletar_categoria(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        if len(context.args) != 2:
            await update.message.reply_text("Formato incorreto. Use: `/delcategoria <tipo> <nome>`\nEx: `/delcategoria gasto academia`")
            return

        tipo, nome = context.args[0].lower(), " ".join(context.args[1:]).lower()
        if tipo not in [GASTO, RENDA]:
            await update.message.reply_text(f"Tipo inválido. Use '{GASTO}' ou '{RENDA}'.")
            return
            
        if delete_category_from_sheet(tipo, nome):
            await update.message.reply_text(f"✅ Categoria '{nome.capitalize()}' removida de '{tipo.capitalize()}'.")
        else:
            await update.message.reply_text(f"⚠️ Categoria '{nome.capitalize()}' não encontrada para o tipo '{tipo}'.")

    except Exception as e:
        await update.message.reply_text(f"❌ Erro ao deletar categoria: {e}")


# --- COMANDOS DE RELATÓRIO --- (extrato e resumo, adaptados do código anterior)
async def extrato(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Esta função pode ser adaptada da versão anterior, pois a lógica de leitura é similar
    await update.message.reply_text("Função de extrato em desenvolvimento.")

async def resumo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Esta função pode ser adaptada da versão anterior, mas agora com ranking de categorias
    await update.message.reply_text("Função de resumo em desenvolvimento.")


# --- FUNÇÃO PRINCIPAL ---

def main() -> None:
    if not TOKEN:
        print("ERRO: O TELEGRAM_TOKEN não foi encontrado.")
        return

    application = Application.builder().token(TOKEN).build()

    # Conversation handler para /gasto e /renda
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("gasto", iniciar_transacao), CommandHandler("renda", iniciar_transacao)],
        states={
            VALOR: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_valor)],
            CATEGORIA: [
                CallbackQueryHandler(receber_categoria_botao),
                MessageHandler(filters.TEXT & ~filters.COMMAND, receber_categoria_texto)
            ],
            DESCRICAO: [
                CommandHandler("pular", pular_descricao),
                MessageHandler(filters.TEXT & ~filters.COMMAND, receber_descricao)
            ],
        },
        fallbacks=[CommandHandler("cancelar", cancelar)],
    )

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("ajuda", ajuda))
    application.add_handler(CommandHandler("categorias", listar_categorias))
    application.add_handler(CommandHandler("addcategoria", adicionar_categoria))
    application.add_handler(CommandHandler("delcategoria", deletar_categoria))
    application.add_handler(CommandHandler("extrato", extrato)) # Adicione as funções completas
    application.add_handler(CommandHandler("resumo", resumo)) # Adicione as funções completas

    print("Bot Ultimate Edition iniciado...")
    application.run_polling()

if __name__ == "__main__":
    main()