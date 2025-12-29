# services/account_service.py
class AccountService:
    def __init__(self, repo, abas):
        self.repo = repo
        self.abas = abas

    def listar(self, user_id):
        return [
            c["conta"]
            for c in self.repo.all(self.abas["CONTAS"])
            if c["user_id"] == user_id
        ]

    def criar(self, user_id, conta, saldo):
        self.repo.append(self.abas["CONTAS"], [user_id, conta, saldo])
