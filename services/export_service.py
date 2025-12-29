# services/export_service.py
import pandas as pd

class ExportService:
    def export(self, df, user_id):
        path = f"/tmp/extrato_{user_id}.csv"
        df.to_csv(path, index=False)
        return path
