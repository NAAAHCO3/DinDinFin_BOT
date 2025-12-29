# services/category_service.py
class CategoryService:
    def __init__(self, repo, abas):
        self.repo = repo
        self.abas = abas

    def listar(self, user_id):
        return [
            c["categoria"]
            for c in self.repo.all(self.abas["CATEGORIAS"])
            if c["user_id"] == user_id
        ]

    def adicionar(self, user_id, categoria):
        self.repo.append(self.abas["CATEGORIAS"], [user_id, categoria])
