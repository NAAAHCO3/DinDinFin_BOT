# services/ml_service.py
import numpy as np
from sklearn.linear_model import LinearRegression
import logging

logger = logging.getLogger(__name__)

class MLService:
    def prever_proximo_gasto(self, df, categoria):
        """Usa regressão linear para prever o próximo gasto baseado no histórico."""
        try:
            df_cat = df[df["categoria"] == categoria].sort_values("data")
            
            if len(df_cat) < 3: # Mínimo de 3 pontos para uma tendência simples
                return None

            # Transforma datas em números ordinais para o modelo
            df_cat["t"] = np.arange(len(df_cat))
            X = df_cat[["t"]]
            y = df_cat["valor"]

            model = LinearRegression()
            model.fit(X, y)

            proximo_indice = len(df_cat)
            previsao = model.predict([[proximo_indice]])[0]
            
            return max(0, previsao) # Nunca retorna gasto negativo
        except Exception as e:
            logger.error(f"Erro na predição de ML: {e}")
            return None