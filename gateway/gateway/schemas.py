from marshmallow import Schema, fields


class CreateOrderDetailSchema(Schema):
    product_id = fields.Str(required=True)
    price = fields.Decimal(as_string=True, required=True)
    quantity = fields.Int(required=True)


class CreateOrderSchema(Schema):
    order_details = fields.Nested(
        CreateOrderDetailSchema, many=True, required=True
    )


class ProductSchema(Schema):
    id = fields.Str(required=True)
    title = fields.Str(required=True)
    maximum_speed = fields.Int(required=True)
    in_stock = fields.Int(required=True)
    passenger_capacity = fields.Int(required=True)


class UpdateProductSchema(Schema):
    title = fields.Str()
    maximum_speed = fields.Int()
    in_stock = fields.Int()
    passenger_capacity = fields.Int()
    class Meta:
        unknown = 'RAISE'



class GetOrderSchema(Schema):

    class OrderDetail(Schema):
        id = fields.Int()
        quantity = fields.Int()
        product_id = fields.Str()
        image = fields.Str()
        price = fields.Decimal(as_string=True)
        product = fields.Nested(ProductSchema, many=False)

    id = fields.Int()
    order_details = fields.Nested(OrderDetail, many=True)


class ListOrderResponseSchema(Schema):

    class ListOrderDetail(Schema):
        id = fields.Int()
        quantity = fields.Int()
        product_id = fields.Str()
        image = fields.Str()
        price = fields.Decimal(as_string=True)

    id = fields.Int()
    order_details = fields.Nested(ListOrderDetail, many=True)


class ListOrdersRequestSchema(Schema):
    ids = fields.List(fields.Str(), required=False)
    page = fields.Int(missing=1)
    per_page = fields.Int(missing=10)