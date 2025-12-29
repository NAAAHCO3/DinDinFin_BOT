from repositories.sheets_repository import SheetsRepository
from services.transaction_service import TransactionService
from services.category_service import CategoryService
from services.account_service import AccountService
from services.budget_service import BudgetService
from services.ml_service import MLService
from services.export_service import ExportService
from config import SHEET_NAME, ABAS

repo = SheetsRepository(SHEET_NAME)

# Nomes completos para os handlers
transaction_service = TransactionService(repo, ABAS)
category_service = CategoryService(repo, ABAS)
account_service = AccountService(repo, ABAS)
budget_service = BudgetService(repo, ABAS)
ml_service = MLService()
export_service = ExportService()

# Mantendo as siglas para compatibilidade
ts = transaction_service
cs = category_service
as_svc = account_service
bs = budget_service