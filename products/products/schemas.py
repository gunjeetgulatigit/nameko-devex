from marshmallow import Schema, fields


class Product(Schema):
    id = fields.Str(required=True)
    title = fields.Str()
    passenger_capacity = fields.Int()
    maximum_speed = fields.Int()
    in_stock = fields.Int()
