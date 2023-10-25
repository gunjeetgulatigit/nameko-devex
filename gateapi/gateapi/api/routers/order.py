from os import name
from fastapi import APIRouter, status, HTTPException
from fastapi.params import Depends
from typing import List
from gateapi.api import schemas
from gateapi.api.dependencies import get_rpc, config
from .exceptions import OrderNotFound

router = APIRouter(
    prefix="/orders",
    tags=['Orders']
)


@router.get("/{order_id}", status_code=status.HTTP_200_OK)
def get_order(order_id: int, rpc=Depends(get_rpc)):
    try:
        return _get_order(order_id, rpc)
    except OrderNotFound as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error)
        )


def _get_order(order_id, nameko_rpc):
    # Retrieve order data from the orders service.
    # Note - this may raise a remote exception that has been mapped to
    # raise``OrderNotFound``
    with nameko_rpc.next() as nameko:
        order = nameko.orders.get_order(order_id)

    # Retrieve all products from the products service
    with nameko_rpc.next() as nameko:
        product_map = {prod['id']: prod for prod in nameko.products.list()}

    # get the configured image root
    image_root = config['PRODUCT_IMAGE_ROOT']

    # Enhance order details with product and image details.
    for item in order['order_details']:
        product_id = item['product_id']

        item['product'] = product_map[product_id]
        # Construct an image url.
        item['image'] = '{}/{}.jpg'.format(image_root, product_id)

    return order


@router.post("", status_code=status.HTTP_200_OK, response_model=schemas.CreateOrderSuccess)
def create_order(request: schemas.CreateOrder, rpc=Depends(get_rpc)):
    id_ = _create_order(request.dict(), rpc)
    return {
        'id': id_
    }


def _create_order(order_data, nameko_rpc):
    # check order product ids are valid
    with nameko_rpc.next() as nameko:
        valid_product_ids = {prod['id'] for prod in nameko.products.list()}
        for item in order_data['order_details']:
            if item['product_id'] not in valid_product_ids:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail=f"Product with id {item['product_id']} not found"
                                    )
        # Call orders-service to create the order.
        result = nameko.orders.create_order(
            order_data['order_details']
        )
        return result['id']


@router.get("/list", status_code=status.HTTP_200_OK)
def list_orders(ids: List[str] = Body(default=None),
                page: int = Body(default=1),
                per_page: int = Body(default=10),
                rpc=Depends(get_rpc)):
    try:
        return _list_orders(ids, page, per_page, rpc)
    except OrderNotFound as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error)
        )


def _list_orders(ids, page, per_page, nameko_rpc):
    if ids:
        with nameko_rpc.next() as nameko:
            orders = nameko.orders.list_orders(ids, page, per_page)
    else:
        with nameko_rpc.next() as nameko:
            orders = nameko.orders.list_orders(page=page, per_page=per_page)

    image_root = config['PRODUCT_IMAGE_ROOT']
    for order in orders:
        for item in order['order_details']:
            product_id = item['product_id']
            item['image'] = '{}/{}.jpg'.format(image_root, product_id)

    return orders
