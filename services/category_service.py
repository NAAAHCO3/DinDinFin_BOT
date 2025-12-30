# services/category_service.py
import logging

logger = logging.getLogger(__name__)

class CategoryService:
    def __init__(self, repo, abas):
        self.repo = repo
        self.abas = abas

    def listar(self, user_id):
        try:
            dados = self.repo.all(self.abas["CATEGORIAS"])
            return [
                str(c["categoria"]) for c in dados 
                if str(c.get("user_id")) == str(user_id)
            ]
        except Exception as e:
            logger.error(f"Erro ao listar categorias: {e}")
            return []

    def adicionar(self, user_id, categoria):
        try:
            self.repo.append(self.abas["CATEGORIAS"], [str(user_id), str(categoria)])
            return True
        except Exception as e:
            logger.error(f"Erro ao adicionar categoria: {e}")
            raise e