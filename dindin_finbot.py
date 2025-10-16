# -*- coding: utf-8 -*-
import os
import gspread
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- CONFIGURAÇÕES IMPORTANTES ---

# 1. LEITURA SEGURA DO TOKEN (NÃO ALTERE ESTA LINHA)
#    Vá em "Environment" no Render e crie a variável de ambiente TELEGRAM_TOKEN
TOKEN = os.getenv("TELEGRAM_TOKEN")

# 2. NOME DA SUA PLANILHA GOOGLE
#    !! IMPORTANTE !! Substitua o texto abaixo pelo nome EXATO da sua planilha.
NOME_DA_PLANILHA = "DinDinFinBOT" 

# --- FUNÇÕES DO BOT ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Envia uma mensagem de boas-vindas quando o comando /start é emitido."""
    await update.message.reply_text('Olá! Eu sou seu bot financeiro. Envie /ajuda para ver os comandos.')

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Repete a mensagem do usuário que não for um comando."""
    await update.message.reply_text(f"Comando não reconhecido. Você disse: {update.message.text}")

async def teste_planilha(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Testa a conexão com a planilha e adiciona uma linha de teste."""
    try:
        await update.message.reply_text("Testando conexão com a planilha, um momento...")

        # Autentica usando o arquivo credentials.json
        gc = gspread.service_account(filename='credentials.json')

        # Abre a planilha usando o nome definido na configuração
        planilha = gc.open(NOME_DA_PLANILHA).sheet1

        # Adiciona uma linha de teste
        linha_teste = ["Teste do Bot", "Conexão OK!", str(datetime.now())]
        planilha.append_row(linha_teste)

        # Envia mensagem de sucesso
        await update.message.reply_text("✅ Sucesso! Uma nova linha foi adicionada à sua planilha.")

    except gspread.exceptions.SpreadsheetNotFound:
        await update.message.reply_text(f"❌ Erro: Planilha não encontrada! Verifique se o nome '{NOME_DA_PLANILHA}' está correto e se você compartilhou a planilha com o email do bot.")
    except Exception as e:
        # Em caso de outros erros, informa o usuário e imprime o erro nos logs do Render
        print(f"Erro ao conectar com a planilha: {e}")
        await update.message.reply_text(f"❌ Falha ao conectar com a planilha. Verifique os logs. Erro: {e}")

def main() -> None:
    """Função principal que inicia o bot."""
    if not TOKEN:
        print("ERRO: O TELEGRAM_TOKEN não foi encontrado. Verifique suas variáveis de ambiente no Render.")
        return

    application = Application.builder().token(TOKEN).build()

    # --- REGISTRO DOS COMANDOS ---
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("testeplanilha", teste_planilha))
    
    # Este handler deve ser um dos últimos, para capturar mensagens que não são comandos
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Inicia o bot
    print("Bot iniciado e escutando...")
    application.run_polling()

if __name__ == "__main__":
    main()