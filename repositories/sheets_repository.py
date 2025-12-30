import os
import json
import gspread
from typing import List, Dict, Any
from google.oauth2.service_account import Credentials


class SheetsRepository:
    """
    Repositório de acesso ao Google Sheets.

    - Suporta credenciais via variável de ambiente (produção)
    - Fallback para arquivo local (desenvolvimento)
    - Cache simples de abas
    """

    SCOPES = (
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    )

    def __init__(self, sheet_name: str, credentials_path: str = "credentials.json"):
        self.sheet_name = sheet_name
        self.credentials_path = credentials_path

        self._client = self._build_client()
        self.sheet = self._client.open(sheet_name)

        # Cache simples de worksheets
        self._abas_cache = {}

    # ============================
    # SETUP
    # ============================
    def _build_client(self) -> gspread.Client:
        """Cria e autentica o cliente gspread."""
        creds = self._load_credentials()
        return gspread.authorize(creds)

    def _load_credentials(self) -> Credentials:
        """
        Carrega credenciais do GCP.

        Prioridade:
        1. Variável de ambiente GCP_CREDENTIALS_JSON
        2. Arquivo local (dev)
        """
        creds_json = os.getenv("GCP_CREDENTIALS_JSON")

        try:
            if creds_json:
                info = json.loads(creds_json)
                return Credentials.from_service_account_info(
                    info, scopes=self.SCOPES
                )

            if not os.path.exists(self.credentials_path):
                raise FileNotFoundError(
                    f"Arquivo de credenciais não encontrado: {self.credentials_path}"
                )

            return Credentials.from_service_account_file(
                self.credentials_path, scopes=self.SCOPES
            )

        except Exception as e:
            raise RuntimeError(
                "❌ Falha ao carregar credenciais do Google Sheets"
            ) from e

    # ============================
    # API PÚBLICA (COMPATÍVEL)
    # ============================
    def get_aba(self, nome_aba: str):
        """Retorna a worksheet (com cache)."""
        if nome_aba not in self._abas_cache:
            self._abas_cache[nome_aba] = self.sheet.worksheet(nome_aba)
        return self._abas_cache[nome_aba]

    def all(self, nome_aba: str) -> List[Dict[str, Any]]:
        """Retorna todos os registros da aba como lista de dicts."""
        return self.get_aba(nome_aba).get_all_records()

    def append(self, nome_aba: str, linha: List[Any]):
        """Adiciona uma linha ao final da aba."""
        return self.get_aba(nome_aba).append_row(linha)
