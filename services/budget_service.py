# services/budget_service.py
import logging

logger = logging.getLogger(__name__)

class BudgetService:
    def __init__(self, repo, abas):
        self.repo = repo
        self.abas = abas

    def alertas(self, user_id, df_gastos):
        """Verifica se gastos ultrapassaram limites definidos."""
        alertas_lista = []
        try:
            orcamentos = self.repo.all(self.abas["ORCAMENTOS"])
            if not orcamentos or df_gastos.empty:
                return []

            for o in orcamentos:
                if str(o.get("user_id")) == str(user_id):
                    cat = str(o["categoria"])
                    limite = float(o["limite"])
                    
                    total_gasto = df_gastos[df_gastos["categoria"] == cat]["valor"].sum()
                    
                    if total_gasto >= limite:
                        alertas_lista.append(f"{cat} (Gasto: R$ {total_gasto:.2f} / Limite: R$ {limite:.2f})")
            
            return alertas_lista
        except Exception as e:
            logger.error(f"Erro ao verificar orçamentos: {e}")
            return []