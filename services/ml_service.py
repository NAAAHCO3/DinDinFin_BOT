import logging
from typing import Optional, Any

import numpy as np
from sklearn.linear_model import LinearRegression

logger = logging.getLogger(__name__)


class MLService:
    """
    Serviço de Machine Learning simples para previsão de gastos.
    """

    MIN_PONTOS = 3

    def prever_proximo_gasto(self, df, categoria: Any) -> Optional[float]:
        """
        Usa regressão linear simples para prever o próximo gasto
        com base no histórico da categoria.

        Retorna:
            Valor previsto (float) ou None se não for possível prever
        """
        try:
            if df is None or df.empty:
                return None

            colunas_necessarias = {"categoria", "valor", "data"}
            if not colunas_necessarias.issubset(df.columns):
                logger.warning("DataFrame inválido para ML")
                return None

            df_cat = (
                df[df["categoria"] == categoria]
                .sort_values("data")
                .copy()  # ⚠️ não altera o DF original
            )

            if len(df_cat) < self.MIN_PONTOS:
                return None

            # Remove valores inválidos
            df_cat = df_cat.dropna(subset=["valor"])
            if df_cat["valor"].nunique() < 2:
                return None  # sem tendência possível

            # Índice temporal simples
            df_cat["t"] = np.arange(len(df_cat))

            X = df_cat[["t"]].values
            y = df_cat["valor"].values

            model = LinearRegression()
            model.fit(X, y)

            proximo_indice = len(df_cat)
            previsao = float(model.predict([[proximo_indice]])[0])

            # Nunca retorna gasto negativo
            return max(0.0, previsao)

        except Exception:
            logger.exception(
                "Erro ao prever gasto | categoria=%s", categoria
            )
            return None
