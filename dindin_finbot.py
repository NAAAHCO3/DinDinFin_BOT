# -*- coding: utf-8 -*-
import os
import gspread
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import io
from flask import Flask
from threading import Thread

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
GASTO, RENDA = "gasto", "renda"

# --- SERVIDOR WEB FLASK PARA MANTER O RENDER ACORDADO ---
app = Flask(__name__)

@app.route('/')
def health_check():
    """Esta rota responde ao Render para dizer que o bot está vivo."""
    return "Bot financeiro está vivo e rodando!", 200

def run_flask():
    """Inicia o servidor Flask em uma porta definida pelo Render."""
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

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

def get_data_as_dataframe(user_id):
    """Busca as transações de um usuário específico como um DataFrame do Pandas."""
    sheet = get_sheet("Transacoes")
    data = sheet.get_all_records()
    if not data:
        return pd.DataFrame()
        
    df = pd.DataFrame(data)
    # Garante que as colunas 'valor' e 'user_id' sejam numéricas
    df['valor'] = pd.to_numeric(df['valor'], errors='coerce')
    df['user_id'] = pd.to_numeric(df['user_id'], errors='coerce')
    # Filtra para o usuário específico
    df_user = df[df['user_id'] == user_id].copy()
    # Garante que a coluna 'data' seja do tipo datetime
    if not df_user.empty and 'data' in df_user.columns:
        df_user['data'] = pd.to_datetime(df_user['data'], errors='coerce')
    return df_user

# --- COMANDOS PRINCIPAIS (/start, /ajuda) ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [["/gasto", "/renda"], ["/resumo", "/extrato"], ["/categorias", "/ajuda"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        'Olá! Bem-vindo ao seu Assistente Financeiro !\n\n'
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
    context.user_data['tipo'] = GASTO if update.message.text.startswith('/gasto') else RENDA
    await update.message.reply_text(f"Qual o valor da transação?")
    return VALOR

async def receber_valor(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
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
    context.user_data['categoria'] = update.message.text.lower()
    await update.message.reply_text("Agora, adicione uma descrição (ou digite /pular).")
    return DESCRICAO

async def receber_descricao(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['descricao'] = update.message.text
    return await finalizar_transacao(update, context)

async def pular_descricao(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['descricao'] = ""
    return await finalizar_transacao(update, context)

async def finalizar_transacao(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        sheet = get_sheet("Transacoes")
        dados = context.user_data
        nova_linha = [str(datetime.now().date()), dados['tipo'], dados['valor'], dados['categoria'], dados.get('descricao', ''), update.effective_user.id]
        sheet.append_row(nova_linha)
        tipo_str = "Gasto" if dados['tipo'] == GASTO else "Renda"
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"✅ {tipo_str} de R${dados['valor']:.2f} em '{dados['categoria'].capitalize()}' registrado com sucesso!")
    except Exception as e:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"❌ Erro ao salvar: {e}")
    context.user_data.clear()
    return ConversationHandler.END

async def cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
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
        if len(context.args) < 2:
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
        if len(context.args) < 2:
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

# --- COMANDOS DE RELATÓRIO COMPLETOS ---
async def extrato(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        df_user = get_data_as_dataframe(update.effective_user.id)
        if df_user.empty:
            await update.message.reply_text("Nenhuma transação encontrada.")
            return

        df_user = df_user.sort_values(by='data', ascending=False).head(10)

        extrato_text = "📜 **Últimas 10 Transações:**\n\n"
        for _, row in df_user.iterrows():
            tipo_emoji = "💰" if row['tipo'] == 'renda' else "💸"
            valor = f"R${row['valor']:.2f}"
            categoria_str = row['categoria'].capitalize()
            data_formatada = row['data'].strftime('%d/%m/%Y') if pd.notna(row['data']) else "N/A"
            extrato_text += f"{tipo_emoji} {data_formatada} - **{valor}** em *{categoria_str}*\n"
        
        await update.message.reply_text(extrato_text, parse_mode='Markdown')
    except Exception as e:
        print(f"Erro ao gerar extrato: {e}")
        await update.message.reply_text(f"❌ Ocorreu um erro ao gerar o extrato. Erro: {e}")

async def resumo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        await update.message.reply_text("Gerando resumo, isso pode levar um momento...")
        df_user = get_data_as_dataframe(update.effective_user.id)
        if df_user.empty:
            await update.message.reply_text("Nenhuma transação encontrada para gerar resumo.")
            return

        target_month, target_year = datetime.now().month, datetime.now().year
        if context.args:
            try:
                month_year_str = context.args[0]
                target_month, target_year = map(int, month_year_str.split('/'))
            except (ValueError, IndexError):
                await update.message.reply_text("❌ Formato de data inválido. Use `MM/AAAA` (ex: `09/2025`)")
                return
        
        df_mes = df_user[(df_user['data'].dt.month == target_month) & (df_user['data'].dt.year == target_year)].copy()
        if df_mes.empty:
            await update.message.reply_text(f"Nenhuma transação encontrada para {target_month:02d}/{target_year}.")
            return

        total_gastos = df_mes[df_mes['tipo'] == 'gasto']['valor'].sum()
        total_rendas = df_mes[df_mes['tipo'] == 'renda']['valor'].sum()
        saldo = total_rendas - total_gastos
        
        gastos_por_categoria = df_mes[df_mes['tipo'] == 'gasto'].groupby('categoria')['valor'].sum().sort_values(ascending=False)
        
        resumo_text = f"📊 **Resumo Financeiro - {target_month:02d}/{target_year}**\n\n"
        resumo_text += f"🟢 *Rendas:* `R$ {total_rendas:.2f}`\n"
        resumo_text += f"🔴 *Gastos:* `R$ {total_gastos:.2f}`\n"
        resumo_text += f"🔵 *Saldo do Mês:* `R$ {saldo:.2f}`\n\n"
        
        if not gastos_por_categoria.empty:
            resumo_text += "🏆 **Top 5 Categorias de Gastos:**\n"
            for categoria, valor in gastos_por_categoria.head(5).items():
                resumo_text += f" - `{categoria.capitalize()}: R$ {valor:.2f}`\n"
        
        await update.message.reply_text(resumo_text, parse_mode='Markdown')

        if not gastos_por_categoria.empty:
            plt.style.use('seaborn-v0_8-pastel')
            fig, ax = plt.subplots(figsize=(8, 6), subplot_kw=dict(aspect="equal"))
            wedges, texts, autotexts = ax.pie(gastos_por_categoria, autopct='%1.1f%%', startangle=90, pctdistance=0.85)
            plt.setp(autotexts, size=8, weight="bold")
            ax.legend(wedges, [f'{cat.capitalize()} (R${val:.2f})' for cat, val in gastos_por_categoria.items()], title="Categorias", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
            ax.set_title(f"Distribuição de Gastos ({target_month:02d}/{target_year})", weight="bold")
            
            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight')
            buf.seek(0)
            plt.close(fig)
            await update.message.reply_photo(photo=buf)
        else:
            await update.message.reply_text("Não há gastos para gerar o gráfico neste período.")
    except Exception as e:
        print(f"Erro ao gerar resumo: {e}")
        await update.message.reply_text(f"❌ Ocorreu um erro ao gerar o resumo. Erro: {e}")

# --- FUNÇÃO PRINCIPAL ---
def main() -> None:
    if not TOKEN:
        print("ERRO CRÍTICO: O TELEGRAM_TOKEN não foi encontrado nas variáveis de ambiente.")
        return

    # Inicia o servidor Flask em uma thread separada para manter o Render "saudável"
    print("Iniciando o servidor Flask para health check...")
    flask_thread = Thread(target=run_flask)
    flask_thread.start()
    
    application = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("gasto", iniciar_transacao), CommandHandler("renda", iniciar_transacao)],
        states={
            VALOR: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_valor)],
            CATEGORIA: [CallbackQueryHandler(receber_categoria_botao), MessageHandler(filters.TEXT & ~filters.COMMAND, receber_categoria_texto)],
            DESCRICAO: [CommandHandler("pular", pular_descricao), MessageHandler(filters.TEXT & ~filters.COMMAND, receber_descricao)],
        },
        fallbacks=[CommandHandler("cancelar", cancelar)],
    )

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("ajuda", ajuda))
    application.add_handler(CommandHandler("categorias", listar_categorias))
    application.add_handler(CommandHandler("addcategoria", adicionar_categoria))
    application.add_handler(CommandHandler("delcategoria", deletar_categoria))
    application.add_handler(CommandHandler("extrato", extrato))
    application.add_handler(CommandHandler("resumo", resumo))

    print("Bot Ultimate Edition iniciado e escutando por mensagens...")
    application.run_polling()

if __name__ == "__main__":
    main()