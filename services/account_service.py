# services/account_service.py
import logging

logger = logging.getLogger(__name__)

class AccountService:
    def __init__(self, repo, abas):
        self.repo = repo
        self.abas = abas

    def listar(self, user_id):
        """Retorna lista de nomes de contas para um usuário específico."""
        try:
            dados = self.repo.all(self.abas["CONTAS"])
            return [
                str(c["conta"]) for c in dados 
                if str(c.get("user_id")) == str(user_id)
            ]
        except Exception as e:
            logger.error(f"Erro ao listar contas: {e}")
            return []

    def criar(self, user_id, conta, saldo):
        """Cria uma nova conta com saldo inicial."""
        try:
            # Garante que o saldo seja gravado como número na planilha
            valor_num = float(str(saldo).replace(",", "."))
            self.repo.append(self.abas["CONTAS"], [str(user_id), str(conta), valor_num])
            return True
        except Exception as e:
            logger.error(f"Erro ao criar conta: {e}")
            raise e