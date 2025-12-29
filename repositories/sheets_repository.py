import gspread
import os
import json
from google.oauth2.service_account import Credentials

class SheetsRepository:
    def __init__(self, sheet_name):
        self.sheet_name = sheet_name
        self.scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        self._sheet = None # Não abre a conexão ainda

    @property
    def sheet(self):
        """Abre a planilha apenas quando for realmente necessária (Lazy Loading)"""
        if self._sheet is None:
            env_creds = os.getenv("GCP_CREDENTIALS_JSON")
            if env_creds:
                info = json.loads(env_creds)
                creds = Credentials.from_service_account_info(info, scopes=self.scopes)
            else:
                creds = Credentials.from_service_account_file("credentials.json", scopes=self.scopes)
            
            client = gspread.authorize(creds)
            self._sheet = client.open(self.sheet_name)
        return self._sheet