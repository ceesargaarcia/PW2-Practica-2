from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, HttpUrl, field_validator


# ── Nested creator info (mirrors Mongoose populate) ───────────────────────────

class CreatedByInfo(BaseModel):
    username: str


# ── Request schemas ───────────────────────────────────────────────────────────

class ProductCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=256)
    description: str = Field(..., min_length=1, max_length=2048)
    price: float = Field(..., ge=0)
    category: str = Field(..., min_length=1, max_length=128)
    stock: int = Field(default=0, ge=0)
    active: bool = True
    image_url: str = Field(
        default="https://placehold.co/400x300?text=Producto",
        alias="imageUrl",
    )

    model_config = {"populate_by_name": True}


class ProductUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=256)
    description: Optional[str] = Field(None, min_length=1, max_length=2048)
    price: Optional[float] = Field(None, ge=0)
    category: Optional[str] = Field(None, min_length=1, max_length=128)
    stock: Optional[int] = Field(None, ge=0)
    active: Optional[bool] = None
    image_url: Optional[str] = Field(None, alias="imageUrl")

    model_config = {"populate_by_name": True}


# ── Response schema ───────────────────────────────────────────────────────────

class ProductResponse(BaseModel):
    """Mirrors the Mongoose document shape expected by the Svelte frontend."""

    id: str = Field(alias="_id")
    name: str
    description: str
    price: float
    category: str
    stock: int
    active: bool
    image_url: str = Field(alias="imageUrl")
    created_by: Optional[str | CreatedByInfo] = Field(None, alias="createdBy")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")

    model_config = {"populate_by_name": True, "from_attributes": True}

    @classmethod
    def from_orm_obj(cls, product, creator_username: str | None = None) -> "ProductResponse":
        created_by_val = (
            CreatedByInfo(username=creator_username)
            if creator_username
            else product.created_by
        )
        return cls(
            _id=product.id,
            name=product.name,
            description=product.description,
            price=product.price,
            category=product.category,
            stock=product.stock,
            active=product.active,
            imageUrl=product.image_url,
            createdBy=created_by_val,
            createdAt=product.created_at,
            updatedAt=product.updated_at,
        )
