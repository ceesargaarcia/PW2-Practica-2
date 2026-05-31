"""Product service — catalogue CRUD business logic."""

from sqlalchemy.orm import Session

from core.exceptions import NotFoundError
from repositories.product_repository import ProductRepository
from repositories.user_repository import UserRepository
from schemas.product import ProductResponse


class ProductService:
    def __init__(self, db: Session):
        self._repo = ProductRepository(db)
        self._user_repo = UserRepository(db)

    def _enrich(self, product) -> ProductResponse:
        """Attach creator username when available (mirrors Mongoose populate)."""
        creator_username: str | None = None
        if product.created_by:
            creator = self._user_repo.get_by_id(product.created_by)
            if creator:
                creator_username = creator.username
        return ProductResponse.from_orm_obj(product, creator_username)

    def get_all(self) -> list[ProductResponse]:
        return [self._enrich(p) for p in self._repo.get_all()]

    def get_one(self, product_id: str) -> ProductResponse:
        product = self._repo.get_by_id(product_id)
        if not product:
            raise NotFoundError("Producto no encontrado")
        return self._enrich(product)

    def create(
        self,
        name: str,
        description: str,
        price: float,
        category: str,
        stock: int,
        active: bool,
        image_url: str,
        creator_id: str | None,
    ) -> ProductResponse:
        product = self._repo.create(
            name=name,
            description=description,
            price=price,
            category=category,
            stock=stock,
            active=active,
            image_url=image_url,
            created_by=creator_id,
        )
        return self._enrich(product)

    def update(self, product_id: str, data: dict) -> ProductResponse:
        product = self._repo.get_by_id(product_id)
        if not product:
            raise NotFoundError("Producto no encontrado")

        # Map camelCase keys from the frontend to snake_case DB columns
        field_map = {"imageUrl": "image_url"}
        normalized: dict = {}
        for key, value in data.items():
            if value is None:
                continue
            normalized[field_map.get(key, key)] = value

        updated = self._repo.update(product, normalized)
        return self._enrich(updated)

    def delete(self, product_id: str) -> None:
        product = self._repo.get_by_id(product_id)
        if not product:
            raise NotFoundError("Producto no encontrado")
        self._repo.delete(product)
