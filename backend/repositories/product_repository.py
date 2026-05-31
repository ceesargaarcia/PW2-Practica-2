"""Product repository — all DB access for the Product model lives here."""

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from models.product import Product


class ProductRepository:
    def __init__(self, db: Session):
        self._db = db

    # ── Queries ───────────────────────────────────────────────────────────────

    def get_by_id(self, product_id: str) -> Optional[Product]:
        return self._db.get(Product, product_id)

    def get_all(self) -> list[Product]:
        return (
            self._db.query(Product)
            .order_by(Product.created_at.desc())
            .all()
        )

    # ── Commands ──────────────────────────────────────────────────────────────

    def create(
        self,
        name: str,
        description: str,
        price: float,
        category: str,
        stock: int = 0,
        active: bool = True,
        image_url: str = "https://placehold.co/400x300?text=Producto",
        created_by: str | None = None,
    ) -> Product:
        product = Product(
            id=str(uuid.uuid4()),
            name=name,
            description=description,
            price=price,
            category=category,
            stock=stock,
            active=active,
            image_url=image_url,
            created_by=created_by,
        )
        self._db.add(product)
        self._db.commit()
        self._db.refresh(product)
        return product

    def update(self, product: Product, data: dict) -> Product:
        """Apply a dict of fields to the product and persist."""
        for field, value in data.items():
            if value is not None:
                setattr(product, field, value)
        product.updated_at = datetime.now(timezone.utc)
        self._db.commit()
        self._db.refresh(product)
        return product

    def delete(self, product: Product) -> None:
        self._db.delete(product)
        self._db.commit()
