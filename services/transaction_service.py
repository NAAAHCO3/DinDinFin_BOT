# services/transaction_service.py
from datetime import datetime
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class TransactionService:
    def __init__(self, repo, abas):
        self.repo = repo
        self.abas = abas

    def registrar(self, user_id, tipo, valor, categoria, conta, descricao):
        try:
            data_formatada = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            valor_num = float(str(valor).replace(",", "."))
            
            self.repo.append(
                self.abas["TRANSACOES"],
                [data_formatada, str(user_id), str(tipo), valor_num, str(categoria), str(conta), str(descricao)]
            )
        except Exception as e:
            logger.error(f"Erro ao registrar transação: {e}")
            raise e

    def df_usuario(self, user_id):
        """Retorna um DataFrame limpo com as transações do usuário."""
        try:
            dados = self.repo.all(self.abas["TRANSACOES"])
            if not dados:
                return pd.DataFrame()
                
            df = pd.DataFrame(dados)
            # Garante que user_id seja string para comparação
            df["user_id"] = df["user_id"].astype(str)
            df = df[df["user_id"] == str(user_id)].copy()
            
            if not df.empty:
                df["data"] = pd.to_datetime(df["data"])
                df["valor"] = pd.to_numeric(df["valor"], errors='coerce').fillna(0)
            
            return df
        except Exception as e:
            logger.error(f"Erro ao processar DataFrame do usuário: {e}")
            return pd.DataFrame()