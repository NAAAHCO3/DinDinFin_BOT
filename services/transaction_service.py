from datetime import datetime, timezone
from typing import Any
import pandas as pd
import logging

logger = logging.getLogger(__name__)


class TransactionService:
    """
    Serviço responsável por registrar e consultar transações financeiras.
    """

    TIPOS_VALIDOS = {"gasto", "renda"}

    def __init__(self, repo, abas: dict):
        self.repo = repo
        self.abas = abas

    # ============================
    # REGISTRO
    # ============================
    def registrar(
        self,
        user_id: Any,
        tipo: str,
        valor: Any,
        categoria: str,
        conta: str,
        descricao: str
    ) -> bool:
        """
        Registra uma transação financeira.

        Retorna:
            True em caso de sucesso
        """
        try:
            tipo = str(tipo).lower().strip()
            if tipo not in self.TIPOS_VALIDOS:
                raise ValueError("Tipo de transação inválido")

            valor_num = self._normalizar_valor(valor)

            data_formatada = datetime.now(timezone.utc).strftime(
                "%Y-%m-%d %H:%M:%S"
            )

            self.repo.append(
                self.abas["TRANSACOES"],
                [
                    data_formatada,
                    str(user_id),
                    tipo,
                    valor_num,
                    str(categoria).strip(),
                    str(conta).strip(),
                    str(descricao).strip(),
                ]
            )

            logger.info(
                "Transação registrada | user_id=%s tipo=%s valor=%.2f",
                user_id, tipo, valor_num
            )

            return True

        except Exception:
            logger.exception(
                "Erro ao registrar transação | user_id=%s", user_id
            )
            raise  # mantém stack trace

    # ============================
    # CONSULTA
    # ============================
    def df_usuario(self, user_id: Any) -> pd.DataFrame:
        """
        Retorna um DataFrame limpo contendo as transações do usuário.
        """
        try:
            dados = self.repo.all(self.abas["TRANSACOES"])
            if not dados:
                return pd.DataFrame()

            df = pd.DataFrame(dados)

            colunas_necessarias = {
                "data", "user_id", "tipo",
                "valor", "categoria", "conta", "descricao"
            }
            if not colunas_necessarias.issubset(df.columns):
                logger.warning("Estrutura inválida de transações")
                return pd.DataFrame()

            df["user_id"] = df["user_id"].astype(str)
            df = df[df["user_id"] == str(user_id)].copy()

            if df.empty:
                return pd.DataFrame()

            df["data"] = pd.to_datetime(df["data"], errors="coerce")
            df["valor"] = (
                pd.to_numeric(df["valor"], errors="coerce")
                .fillna(0.0)
            )

            return df

        except Exception:
            logger.exception(
                "Erro ao gerar DataFrame do usuário | user_id=%s", user_id
            )
            return pd.DataFrame()

    # ============================
    # UTIL
    # ============================
    @staticmethod
    def _normalizar_valor(valor: Any) -> float:
        """Converte valor monetário para float seguro."""
        try:
            return float(str(valor).replace(",", "."))
        except Exception:
            raise ValueError(f"Valor inválido: {valor}")
