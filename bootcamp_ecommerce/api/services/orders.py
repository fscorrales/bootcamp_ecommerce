__all__ = ["OrdersServiceDependency", "OrdersService"]


from typing import Annotated

from fastapi import Depends, HTTPException, status
from pydantic_mongo import PydanticObjectId

from ..__common_deps import QueryParamsDependency
from ..config import COLLECTIONS, db
from ..models import Order, CreateOrderItem, StoredOrder, OrderStatus, OrderItem


class OrdersService:
    assert (collection_name := "orders") in COLLECTIONS
    collection = db[collection_name]



    @classmethod
    def shopping_cart(cls, order: CreateOrderItem):
        product = order.model_dump(exclude={"customer_id"})
        pending_order = cls.get_pending_order_by_customer_id(order.customer_id)
        if not pending_order:
            order = Order(
                customer_id=order.customer_id,
                products=[],
                status=OrderStatus.pending,
            )
            document = cls.collection.insert_one(order)
            pending_order = str(document.inserted_id)
        document =cls.add_product(pending_order, product)
        if document:
            return document
        return None
    
    @classmethod
    def add_item(cls, id: PydanticObjectId, product: OrderItem):
        document = cls.collection.find_one_and_update(
            {"_id": id},
            {"$push": {"products": product}},
            return_document=True,
        )
        if document:
            return StoredOrder.model_validate(document).model_dump()
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
            )

    @classmethod
    def delete_item(cls, id: PydanticObjectId, product: OrderItem):
        document = cls.collection.find_one_and_update(
            {"_id": id},
            {"$pull": {"products": product}},
            return_document=True,
        )
        if document:
            return StoredOrder.model_validate(document).model_dump()
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
            )

    @classmethod
    def update_shopping_cart_status(cls, id: PydanticObjectId, status: OrderStatus):
        document = cls.collection.find_one_and_update(
            {"_id": id, "status": OrderStatus.pending},
            {"$set": {"status": status}},
            return_document=True,
        )
        if document:
            return StoredOrder.model_validate(document).model_dump()
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
            )

    @classmethod
    def get_all(cls, params: QueryParamsDependency):
        return [
            StoredOrder.model_validate(order).model_dump()
            for order in params.query_collection(cls.collection)
        ]

    @classmethod
    def get_one(cls, id: PydanticObjectId, authorized_user_id: PydanticObjectId | None):
        filter_criteria: dict = {"_id": id}
        if authorized_user_id:
            filter_criteria.update(
                {
                    "$or": [
                        {"customer_id": authorized_user_id},
                        {"seller_id": authorized_user_id},
                    ]
                }
            )

        if db_order := cls.collection.find_one(filter_criteria):
            return StoredOrder.model_validate(db_order).model_dump()
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
            )

    @classmethod
    def get_one_by_customer_id(cls, customer_id: PydanticObjectId, status: OrderStatus | None):
        filter_criteria: dict = {"customer_id": id}
        if status:
            filter_criteria.update(
                {"status": status}
            )

        if db_order := cls.collection.find_one(filter_criteria):
            return StoredOrder.model_validate(db_order).model_dump()
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
            )

    @classmethod
    def get_pending_order_by_customer_id(cls, authorized_user_id: PydanticObjectId | None):
        filter_criteria: dict = {"status": "pending"}
        if authorized_user_id:
            filter_criteria.update(
                {
                    "$or": [
                        {"customer_id": authorized_user_id},
                        {"seller_id": authorized_user_id},
                    ]
                }
            )
        if db_order := cls.collection.find_one(filter_criteria):
            return StoredOrder.model_validate(db_order).model_dump(include={"_id"})
        else:
            return None
        

OrdersServiceDependency = Annotated[OrdersService, Depends()]
