"""
Container de Dependências do DinDinFin

- Centraliza instâncias globais
- Mantém compatibilidade com handlers antigos
- Facilita evolução para testes, banco e cloud
"""

from repositories.sheets_repository import SheetsRepository
from services.transaction_service import TransactionService
from services.category_service import CategoryService
from services.account_service import AccountService
from services.budget_service import BudgetService
from services.ml_service import MLService
from services.export_service import ExportService
from config import SHEET_NAME, ABAS


# ============================
# REPOSITÓRIO ÚNICO
# ============================
def _build_repository():
    """Cria o repositório principal (Google Sheets)."""
    return SheetsRepository(SHEET_NAME)


_repo = _build_repository()


# ============================
# SERVICES (INSTÂNCIAS ÚNICAS)
# ============================
transaction_service: TransactionService = TransactionService(_repo, ABAS)
category_service: CategoryService = CategoryService(_repo, ABAS)
account_service: AccountService = AccountService(_repo, ABAS)
budget_service: BudgetService = BudgetService(_repo, ABAS)

ml_service: MLService = MLService()
export_service: ExportService = ExportService()


# ============================
# ALIASES (BACKWARD COMPAT)
# ============================
# ⚠️ NÃO REMOVER — usados por handlers antigos
ts = transaction_service
cs = category_service
as_svc = account_service
bs = budget_service
