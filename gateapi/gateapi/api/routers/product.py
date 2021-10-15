from fastapi import APIRouter, status, HTTPException
from fastapi.params import Depends
from gateapi.api.dependencies import get_rpc
from gateapi.api import schemas
from .exceptions import ProductNotFound

router = APIRouter(
    prefix = "/products",
    tags = ["Products"]
)

@router.get("/{product_id}", status_code=status.HTTP_200_OK, response_model=schemas.Product)
def get_product(product_id: str, rpc = Depends(get_rpc)):
    try: 
        with rpc.next() as nameko:
            return nameko.products.get(product_id)
    except ProductNotFound as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error)
        )

@router.post("", status_code=status.HTTP_200_OK, response_model=schemas.CreateProductSuccess)
def create_product(request: schemas.Product, rpc = Depends(get_rpc)):
    with rpc.next() as nameko:
        nameko.products.create(request.dict())
        return {
            "id": request.id
        }
