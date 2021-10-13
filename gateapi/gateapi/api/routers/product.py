from fastapi import APIRouter, status, HTTPException
from fastapi.params import Depends
from gateapi.api.dependencies import NamekoRPCPoolDep, nameko_rpc
from gateapi.api import schemas
from nameko.exceptions import RemoteError
from .exceptions import ProductNotFound

router = APIRouter(
    prefix = "/products",
    tags = ["Products"]
)

@router.get("/{product_id}", status_code=status.HTTP_200_OK, response_model=schemas.Product)
def get_product(product_id: str, nameko: NamekoRPCPoolDep = Depends(nameko_rpc)):
    try:   
        return nameko.products.get(product_id)
    except ProductNotFound as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error)
        )

@router.post("", status_code=status.HTTP_200_OK, response_model=schemas.CreateProductSuccess)
def create_product(request: schemas.Product, nameko: NamekoRPCPoolDep = Depends(nameko_rpc)):
    nameko.products.create(request.dict())
    return {
        "id": request.id
    }
