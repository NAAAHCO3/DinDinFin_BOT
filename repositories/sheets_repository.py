# repositories/sheets_repository.py
import gspread
from google.oauth2.service_account import Credentials

class SheetsRepository:
    def __init__(self, sheet_name):
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        creds = Credentials.from_service_account_file(
            "credentials.json", scopes=scopes
        )
        self.client = gspread.authorize(creds)
        self.sheet = self.client.open(sheet_name)

    def get(self, aba):
        return self.sheet.worksheet(aba)

    def all(self, aba):
        return self.get(aba).get_all_records()

    def append(self, aba, row):
        self.get(aba).append_row(row)
