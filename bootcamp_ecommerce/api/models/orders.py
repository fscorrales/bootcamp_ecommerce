__all__ = [
    "OrderStatus", "OrderProducts", "UpdateOrderProduct", 
    "Order", "StoredOrder"
]

from enum import Enum

from pydantic import BaseModel, Field
from pydantic_mongo import PydanticObjectId


class OrderStatus(str, Enum):
    shopping = "shopping"
    completed = "completed"
    cancelled = "cancelled"


class OrderProducts(BaseModel):
    product_id: PydanticObjectId
    price: float
    quantity: int


class UpdateOrderProduct(OrderProducts):
    customer_id: PydanticObjectId


class Order(BaseModel):
    customer_id: PydanticObjectId
    order_products: list[OrderProducts]
    status: OrderStatus = OrderStatus.shopping


class StoredOrder(Order):
    id: PydanticObjectId = Field(alias="_id")
