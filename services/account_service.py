import logging
from typing import List, Any

logger = logging.getLogger(__name__)


class AccountService:
    """
    Serviço responsável por gerenciar contas financeiras do usuário.
    """

    def __init__(self, repo, abas: dict):
        self.repo = repo
        self.abas = abas

    # ============================
    # CONSULTA
    # ============================
    def listar(self, user_id: Any) -> List[str]:
        """
        Retorna a lista de nomes de contas de um usuário.

        Em caso de erro, retorna lista vazia (com log).
        """
        try:
            dados = self.repo.all(self.abas["CONTAS"])

            return [
                str(linha["conta"])
                for linha in dados
                if str(linha.get("user_id")) == str(user_id)
            ]

        except Exception:
            logger.exception("Erro ao listar contas do usuário %s", user_id)
            return []

    # ============================
    # CRIAÇÃO
    # ============================
    def criar(self, user_id: Any, conta: str, saldo: Any) -> bool:
        """
        Cria uma nova conta com saldo inicial.

        Retorna:
            True em caso de sucesso
        Lança:
            Exception em caso de falha crítica
        """
        if not conta or not str(conta).strip():
            raise ValueError("Nome da conta inválido")

        try:
            valor_num = self._normalizar_valor(saldo)

            self.repo.append(
                self.abas["CONTAS"],
                [str(user_id), str(conta).strip(), valor_num]
            )

            logger.info(
                "Conta criada | user_id=%s conta=%s saldo=%.2f",
                user_id, conta, valor_num
            )

            return True

        except Exception:
            logger.exception(
                "Erro ao criar conta | user_id=%s conta=%s", user_id, conta
            )
            raise  # mantém stack trace original

    # ============================
    # UTIL
    # ============================
    @staticmethod
    def _normalizar_valor(valor: Any) -> float:
        """Converte valor monetário para float seguro."""
        try:
            return float(str(valor).replace(",", "."))
        except Exception:
            raise ValueError(f"Saldo inválido: {valor}")
