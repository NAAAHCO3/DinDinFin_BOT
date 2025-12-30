import os
import uuid
import logging
import pandas as pd
from typing import Any

logger = logging.getLogger(__name__)


class ExportService:
    """
    Serviço responsável por exportar dados do usuário.
    """

    BASE_DIR = "/tmp"

    def export(self, df: pd.DataFrame, user_id: Any) -> str:
        """
        Exporta um DataFrame para CSV.

        Retorna:
            Caminho do arquivo gerado
        """
        if df is None or df.empty:
            raise ValueError("DataFrame vazio ou inválido")

        try:
            os.makedirs(self.BASE_DIR, exist_ok=True)

            filename = f"extrato_{user_id}_{uuid.uuid4().hex[:8]}.csv"
            path = os.path.join(self.BASE_DIR, filename)

            df.to_csv(path, index=False)

            logger.info(
                "Arquivo exportado | user_id=%s path=%s rows=%s",
                user_id, path, len(df)
            )

            return path

        except Exception:
            logger.exception(
                "Erro ao exportar arquivo | user_id=%s", user_id
            )
            raise
