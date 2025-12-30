import logging
from typing import List, Any

logger = logging.getLogger(__name__)


class BudgetService:
    """
    Serviço responsável por verificar estouro de orçamento por categoria.
    """

    def __init__(self, repo, abas: dict):
        self.repo = repo
        self.abas = abas

    # ============================
    # ALERTAS
    # ============================
    def alertas(self, user_id: Any, df_gastos) -> List[str]:
        """
        Verifica se os gastos do usuário ultrapassaram os limites definidos.

        Retorna:
            Lista de mensagens de alerta (strings)
        """
        try:
            if df_gastos is None or df_gastos.empty:
                return []

            orcamentos = self.repo.all(self.abas["ORCAMENTOS"])
            if not orcamentos:
                return []

            alertas = []

            for orcamento in orcamentos:
                if str(orcamento.get("user_id")) != str(user_id):
                    continue

                categoria = str(orcamento.get("categoria", "")).strip()
                limite = self._normalizar_valor(orcamento.get("limite"))

                if not categoria or limite <= 0:
                    continue

                total_gasto = self._total_por_categoria(df_gastos, categoria)

                if total_gasto >= limite:
                    alertas.append(
                        f"{categoria} "
                        f"(Gasto: R$ {total_gasto:,.2f} / "
                        f"Limite: R$ {limite:,.2f})"
                    )

            return alertas

        except Exception:
            logger.exception(
                "Erro ao verificar orçamentos | user_id=%s", user_id
            )
            return []

    # ============================
    # UTILITÁRIOS
    # ============================
    @staticmethod
    def _total_por_categoria(df, categoria: str) -> float:
        """Calcula o total gasto de uma categoria específica."""
        try:
            return float(
                df.loc[df["categoria"] == categoria, "valor"].sum()
            )
        except Exception:
            return 0.0

    @staticmethod
    def _normalizar_valor(valor) -> float:
        """Converte valor monetário para float seguro."""
        try:
            return float(str(valor).replace(",", "."))
        except Exception:
            return 0.0
