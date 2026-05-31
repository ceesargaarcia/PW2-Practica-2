from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from db.database import get_db
from middleware.auth_middleware import get_current_user, require_admin
from schemas.product import ProductCreateRequest, ProductResponse, ProductUpdateRequest
from services.product_service import ProductService

router = APIRouter(prefix="/api/products", tags=["products"])


def _svc(db): return ProductService(db)


@router.get("", response_model=list[ProductResponse])
@router.get("/", response_model=list[ProductResponse], include_in_schema=False)
def list_products(
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    return _svc(db).get_all()


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: str,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    return _svc(db).get_one(product_id)


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED, include_in_schema=False)
def create_product(
    body: ProductCreateRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin),
):
    return _svc(db).create(
        name=body.name,
        description=body.description,
        price=body.price,
        category=body.category,
        stock=body.stock,
        active=body.active,
        image_url=body.image_url,
        creator_id=current_user.get("userId"),
    )


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: str,
    body: ProductUpdateRequest,
    db: Session = Depends(get_db),
    _: dict = Depends(require_admin),
):
    data = body.model_dump(exclude_none=True, by_alias=True)
    return _svc(db).update(product_id, data)


@router.delete("/{product_id}")
def delete_product(
    product_id: str,
    db: Session = Depends(get_db),
    _: dict = Depends(require_admin),
):
    _svc(db).delete(product_id)
    return {"message": "Producto eliminado"}
