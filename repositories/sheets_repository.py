import gspread
from google.oauth2.service_account import Credentials

class SheetsRepository:
    def __init__(self, sheet_name):
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        # O arquivo de credenciais deve estar na raiz
        creds = Credentials.from_service_account_file(
            "credentials.json", scopes=scopes
        )
        self.client = gspread.authorize(creds)
        self.sheet = self.client.open(sheet_name)

    def get_aba(self, nome_aba):
        return self.sheet.worksheet(nome_aba)

    def all(self, nome_aba):
        """Lê todos os registros de uma aba (Essencial para os Services)"""
        return self.get_aba(nome_aba).get_all_records()

    def append(self, nome_aba, linha):
        """Adiciona uma nova linha na aba especificada"""
        return self.get_aba(nome_aba).append_row(linha)