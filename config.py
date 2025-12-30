import os
import logging

logger = logging.getLogger(__name__)

# ============================
# AMBIENTE
# ============================
ENV = os.getenv("ENV", "dev").lower()


# ============================
# TELEGRAM
# ============================
BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")

if not BOT_TOKEN:
    logger.warning("⚠️ TELEGRAM_TOKEN não definido")


# ============================
# GOOGLE SHEETS
# ============================
SHEET_NAME = os.getenv("GOOGLE_SHEET_NAME", "DinDinFinBOT")

if not SHEET_NAME:
    logger.warning("⚠️ GOOGLE_SHEET_NAME não definido")


# ============================
# ABAS DA PLANILHA
# ============================
ABAS = {
    "TRANSACOES": os.getenv("ABA_TRANSACOES", "Transacoes"),
    "CATEGORIAS": os.getenv("ABA_CATEGORIAS", "Categorias"),
    "CONTAS": os.getenv("ABA_CONTAS", "Contas"),
    "ORCAMENTOS": os.getenv("ABA_ORCAMENTOS", "Orcamentos"),
}

# Validação básica das chaves esperadas
_ABAS_OBRIGATORIAS = {"TRANSACOES", "CATEGORIAS", "CONTAS", "ORCAMENTOS"}
faltando = _ABAS_OBRIGATORIAS - ABAS.keys()

if faltando:
    raise RuntimeError(f"Configuração ABAS incompleta: {faltando}")


# ============================
# DEBUG (opcional)
# ============================
if ENV == "dev":
    logger.info(f"Config carregada | Sheet: {SHEET_NAME} | Abas: {ABAS}")
