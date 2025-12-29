# services/transaction_service.py
from datetime import datetime
import pandas as pd

class TransactionService:
    def __init__(self, repo, abas):
        self.repo = repo
        self.abas = abas

    def registrar(self, user_id, tipo, valor, categoria, conta, descricao):
        self.repo.append(
            self.abas["TRANSACOES"],
            [
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                user_id, tipo, valor, categoria, conta, descricao
            ]
        )

    def df_usuario(self, user_id):
        df = pd.DataFrame(self.repo.all(self.abas["TRANSACOES"]))
        df["data"] = pd.to_datetime(df["data"])
        return df[df["user_id"] == user_id]
