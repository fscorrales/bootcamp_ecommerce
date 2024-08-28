__all__ = [
    "OrderStatus", "OrderItem", "CreateOrderItem", 
    "DeleteOrderItem", "Order", "StoredOrder"
]

from enum import Enum

from pydantic import BaseModel, Field
from pydantic_mongo import PydanticObjectId
from typing import List 


class OrderStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"
    canceled = "canceled"


class OrderItem(BaseModel):
    product_id: PydanticObjectId
    price: float
    quantity: int


class CreateOrderItem(OrderItem):
    customer_id: PydanticObjectId


class DeleteOrderItem(BaseModel):
    id: PydanticObjectId = Field(alias="_id")
    product_id: PydanticObjectId


class Order(BaseModel):
    customer_id: PydanticObjectId
    products: List[OrderItem]
    status: OrderStatus = OrderStatus.pending


class StoredOrder(Order):
    id: PydanticObjectId = Field(alias="_id")
