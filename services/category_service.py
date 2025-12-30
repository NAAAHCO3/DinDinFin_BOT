import logging
from typing import List, Any

logger = logging.getLogger(__name__)


class CategoryService:
    """
    Serviço responsável por gerenciar categorias de renda e gasto.
    """

    TIPOS_VALIDOS = {"renda", "gasto"}

    def __init__(self, repo, abas: dict):
        self.repo = repo
        self.abas = abas

    # ============================
    # LISTAGEM
    # ============================
    def listar_por_tipo(self, user_id: Any, tipo: str) -> List[str]:
        """
        Lista categorias do usuário filtrando por tipo (renda ou gasto).
        """
        tipo = str(tipo).lower().strip()

        if tipo not in self.TIPOS_VALIDOS:
            logger.warning("Tipo de categoria inválido: %s", tipo)
            return []

        try:
            return [
                str(c.get("categoria")).strip()
                for c in self.repo.all(self.abas["CATEGORIAS"])
                if str(c.get("user_id")) == str(user_id)
                and str(c.get("tipo")).lower() == tipo
                and c.get("categoria")
            ]
        except Exception:
            logger.exception(
                "Erro ao listar categorias | user_id=%s tipo=%s", user_id, tipo
            )
            return []

    # ============================
    # CRIAÇÃO
    # ============================
    def adicionar(self, user_id: Any, categoria: str, tipo: str = "gasto") -> bool:
        """
        Adiciona uma nova categoria.

        Retorna:
            True em caso de sucesso
        """
        tipo = str(tipo).lower().strip()
        categoria = str(categoria).strip()

        if tipo not in self.TIPOS_VALIDOS:
            raise ValueError("Tipo de categoria inválido (use renda ou gasto)")

        if not categoria:
            raise ValueError("Nome da categoria inválido")

        try:
            self.repo.append(
                self.abas["CATEGORIAS"],
                [str(user_id), categoria, tipo]
            )

            logger.info(
                "Categoria adicionada | user_id=%s categoria=%s tipo=%s",
                user_id, categoria, tipo
            )

            return True

        except Exception:
            logger.exception(
                "Erro ao adicionar categoria | user_id=%s categoria=%s tipo=%s",
                user_id, categoria, tipo
            )
            raise
