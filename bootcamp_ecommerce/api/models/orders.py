__all__ = ["OrderItem", "Order", "StoredOrder"]

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


class Order(BaseModel):
    customer_id: PydanticObjectId
    status: OrderStatus = OrderStatus.pending


class OrderUpdate(Order):
    items: List[OrderItem]


class StoredOrder(OrderUpdate):
    id: PydanticObjectId = Field(alias="_id")
