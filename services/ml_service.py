# services/ml_service.py
import numpy as np
from sklearn.linear_model import LinearRegression

class MLService:
    def prever_categoria(self, df, categoria):
        df = df[df["categoria"] == categoria]
        if len(df) < 5:
            return None

        df = df.sort_values("data")
        df["t"] = np.arange(len(df))

        X = df[["t"]]
        y = df["valor"]

        model = LinearRegression()
        model.fit(X, y)

        return model.predict([[len(df) + 5]])[0]
