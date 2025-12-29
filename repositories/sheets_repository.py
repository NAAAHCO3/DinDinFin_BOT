# repositories/sheets_repository.py
import gspread
import os
import json
from google.oauth2.service_account import Credentials

class SheetsRepository:
    def __init__(self, sheet_name):
        scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        
        # Lê o JSON de credenciais da variável de ambiente injetada pelo Cloud Run
        env_creds = os.getenv("GCP_CREDENTIALS_JSON")
        
        if env_creds:
            info = json.loads(env_creds)
            creds = Credentials.from_service_account_info(info, scopes=scopes)
        else:
            creds = Credentials.from_service_account_file("credentials.json", scopes=scopes)
            
        self.client = gspread.authorize(creds)
        self.sheet = self.client.open(sheet_name) # Abre a planilha compartilhada