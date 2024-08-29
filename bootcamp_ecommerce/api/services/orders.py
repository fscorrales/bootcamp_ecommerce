__all__ = ["OrdersServiceDependency", "OrdersService"]


from typing import Annotated, Literal

from fastapi import Depends, HTTPException, status
from pydantic_mongo import PydanticObjectId

from ..__common_deps import QueryParamsDependency, QueryParams
from ..config import COLLECTIONS, db
from ..config.__base_config import logger
from ..models import Order, UpdateOrderItem, StoredOrder, OrderStatus, OrderItem
from bson import ObjectId

class OrdersService:
    assert (collection_name := "orders") in COLLECTIONS
    collection = db[collection_name]

    # Used by seed_database.py 
    @classmethod
    def create_one(cls, order: Order):
        document = cls.collection.insert_one(order.model_dump())
        if document:
            return str(document.inserted_id)
        return None


    @classmethod
    def shopping_cart(cls, order: UpdateOrderItem, remove_from_cart: bool = False):
        product = order.model_dump(exclude={"customer_id"})
        params = QueryParams(
            filter=f"custommer_id={order.customer_id}, status={OrderStatus.pending}"
        )
        pending_order = cls.get_all(params)
        # pending_order = cls.get_one_by_customer_id(
        #     order.customer_id, OrderStatus.pending
        # )
        if not pending_order and not remove_from_cart:
            # order = Order(
            #     customer_id=order.customer_id,
            #     status=OrderStatus.pending,
            # )
            order_dict = order.model_dump(include={"customer_id"}).update(
                {"status": OrderStatus.pending, "products": [product]}
            )
            document = cls.collection.insert_one(order_dict)
            # pending_order = str(document.inserted_id)
        else:
            if remove_from_cart and pending_order:
                document = cls.update_order_item(
                    ObjectId(pending_order.get("id")), product, 'remove'
                )
            else:
                document = cls.update_order_item(
                    ObjectId(pending_order.get("id")), product, "add"
                )
        if document:
            return document
        return None
    
    @classmethod
    def update_order_item(
        cls, id: PydanticObjectId, product: OrderItem, 
        opt: Literal['add', 'remove'] = 'add'
    ):
        if opt == 'add':
            document = cls.collection.find_one_and_update(
                {"_id": id},
                {"$push": {"products": product}},
                return_document=True,
            )
        else:
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

    # @classmethod
    # def remove_item(cls, id: PydanticObjectId, product: OrderItem):
    #     document = cls.collection.find_one_and_update(
    #         {"_id": id},
    #         {"$pull": {"products": product}},
    #         return_document=True,
    #     )
    #     if document:
    #         return StoredOrder.model_validate(document).model_dump()
    #     else:
    #         raise HTTPException(
    #             status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
    #         )

    @classmethod
    def update_shopping_cart_status(cls, id: PydanticObjectId, order_status: OrderStatus):
        document = cls.collection.find_one_and_update(
            {"_id": id, "status": OrderStatus.pending},
            {"$set": {"status": order_status}},
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

    # @classmethod
    # def get_one_by_customer_id(cls, customer_id: str, order_status: OrderStatus | None):
    #     # filter_criteria: dict = {"customer_id": str(customer_id)}
    #     filter_criteria = dict(costumer_id=str(customer_id))
    #     if order_status:
    #         filter_criteria.update(
    #             {"status": order_status}
    #         )
    #     if db_order := cls.collection.find_one(filter_criteria):
    #         return StoredOrder.model_validate(db_order).model_dump()
    #     else:
    #         raise HTTPException(
    #             status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
    #         )
        

OrdersServiceDependency = Annotated[OrdersService, Depends()]