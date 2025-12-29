# services/budget_service.py
class BudgetService:
    def __init__(self, repo, abas):
        self.repo = repo
        self.abas = abas

    def alertas(self, user_id, df_gastos):
        alerts = []
        for o in self.repo.all(self.abas["ORCAMENTOS"]):
            if o["user_id"] == user_id:
                total = df_gastos[
                    df_gastos["categoria"] == o["categoria"]
                ]["valor"].sum()
                if total >= o["limite"]:
                    alerts.append(o["categoria"])
        return alerts
