from nameko.events import EventDispatcher
from nameko.rpc import rpc
from nameko_sqlalchemy import DatabaseSession

from orders.exceptions import NotFound
from orders.models import DeclarativeBase, Order, OrderDetail
from orders.schemas import OrderSchema


class OrdersService:
    name = "orders"

    db = DatabaseSession(DeclarativeBase)
    event_dispatcher = EventDispatcher()

    @rpc
    def get_order(self, order_id):
        order = self.db.query(Order).get(order_id)

        if not order:
            raise NotFound("Order with id {} not found".format(order_id))

        return OrderSchema().dump(order).data

    @rpc
    def create_order(self, order_details):
        order = Order(
            order_details=[
                OrderDetail(
                    product_id=order_detail["product_id"],
                    price=order_detail["price"],
                    quantity=order_detail["quantity"],
                )
                for order_detail in order_details
            ]
        )
        self.db.add(order)
        self.db.commit()

        order = OrderSchema().dump(order).data

        self.event_dispatcher(
            "order_created",
            {
                "order": order,
            },
        )

        return order

    @rpc
    def update_order(self, order):
        order_details = {order_details["id"]: order_details for order_details in order["order_details"]}

        order = self.db.query(Order).get(order["id"])

        for order_detail in order.order_details:
            order_detail.price = order_details[order_detail.id]["price"]
            order_detail.quantity = order_details[order_detail.id]["quantity"]

        self.db.commit()
        return OrderSchema().dump(order).data

    @rpc
    def delete_order(self, order_id):
        order = self.db.query(Order).get(order_id)
        self.db.delete(order)
        self.db.commit()

    @rpc
    def list_orders(self, ids=None, page=1, per_page=10):
        """
        Retrieve a list of orders from the database with optional filtering and pagination.

        Args:
            ids (list): A list of order IDs to filter by (default is None).
            page (int): The page number for pagination (default is 1).
            per_page (int): The number of orders to retrieve per page (default is 10).

        Returns:
            A list of orders in JSON format.

        """
        # Initialize the base query
        query = self.db.query(Order)

        if ids:
            # Filter by order IDs if provided
            query = query.filter(Order.id.in_(ids))

        # Calculate the offset and limit based on pagination parameters
        offset = (page - 1) * per_page
        limit = per_page

        # Execute the query
        orders = query.offset(offset).limit(limit).all()

        if not orders:
            return []

        # Serialize the orders using OrderSchema
        serialized_orders = OrderSchema(many=True).dump(orders).data
        return serialized_orders
