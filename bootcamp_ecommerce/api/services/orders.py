__all__ = ["OrdersServiceDependency", "OrdersService"]


from copy import deepcopy
from typing import Annotated, Literal

from bson import ObjectId
from fastapi import Depends, HTTPException, status
from pydantic_mongo import PydanticObjectId

from ..__common_deps import QueryParamsDependency, QueryParams
from ..config import COLLECTIONS, db, logger
from ..models import Order, UpdateOrderProduct, StoredOrder, OrderStatus, OrderProducts
from ..services import SecurityDependency


def get_orders_by_seller_id_aggregate_query(
    seller_id: PydanticObjectId, pre_filters: dict | None = None
):

    return [
        # Only if we have an order id
        {"$match": pre_filters},
        # Then we need to lookup the products collection
        {
            "$lookup": {
                "from": "products",
                "localField": "order_products.product_id",
                "foreignField": "_id",
                "as": "product",
            }
        },
        # Then we need to unwind the product
        {"$unwind": "$product"},
        # Then we need to filter by the seller
        {"$match": {"product.seller_id": ObjectId(seller_id)}},
        # Finilly we need to remove duplicates
        # and remove the field of the matched product
        {
            "$group": {
                "_id": "$_id",
                "customer_id": {"$first": "$customer_id"},
                "status": {"$first": "$status"},
                "order_products": {"$first": "$order_products"},
            }
        },
    ]


class OrdersService:
    assert (collection_name := "orders") in COLLECTIONS
    collection = db[collection_name]

    # Used by seed_database.py 
    @classmethod
    def create_one(cls, order: Order):
        new_order = order.model_dump()
        new_order["customer_id"] = ObjectId(new_order["customer_id"])
        for product in new_order["order_products"]:
            product["product_id"] = ObjectId(product["product_id"])
        document = cls.collection.insert_one(new_order)
        if document:
            return str(document.inserted_id)
        return None


    @classmethod
    def shopping_cart(cls, order: UpdateOrderProduct, remove_from_cart: bool = False):
        product = order.model_dump(exclude={"customer_id"})
        params = QueryParams(
            filter=f"customer_id={order.customer_id}, status=shopping"
        )
        shopping_order = cls.get_all_shopping(params)
        # pending_order = cls.get_one_by_customer_id(
        #     order.customer_id, OrderStatus.pending
        # )
        logger.info(shopping_order)
        if  len(shopping_order) == 0 and not remove_from_cart:
            order = Order(
                customer_id=order.customer_id,
                products=[product],
                status=OrderStatus.shopping
            )
            # order_dict = order.model_dump(include={"customer_id"})
            # order_dict.update(
            #     {"products": [product], "status": OrderStatus.pending}
            # )
            # order_dict = order_dict.update(
            #     {"status": OrderStatus.pending, "products": [product]}
            # )
            document = cls.collection.insert_one(order.model_dump())
            logger.info(document)
            # pending_order = str(document.inserted_id)
        elif len(shopping_order) > 0:
            id_shopping_order = shopping_order[0].get("id")
            if remove_from_cart:
                document = cls.update_order_product(
                    ObjectId(id_shopping_order), product, 'remove'
                )
            else:
                document = cls.update_order_product(
                    ObjectId(id_shopping_order), product, "add"
                )
        if document:
            return document
        return None

    
    @classmethod
    def update_order_product(
        cls, id: PydanticObjectId, product: OrderProducts, 
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
        logger.info(document)
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
            {"_id": id, "status": OrderStatus.shopping},
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
    def get_all_shopping(cls, params: QueryParamsDependency):
        return [
            StoredOrder.model_validate(order).model_dump()
            for order in params.query_collection(cls.collection)
        ]


    @classmethod
    def get_all(cls, params: QueryParamsDependency, security: SecurityDependency):
        filter_query: dict = {}
        params_filter = deepcopy(params.filter_dict)

        if security.auth_user_role == "customer":
            filter_query.update(
                {"customer_id": security.auth_user_id},
            )

        if security.auth_user_role != "seller" and "seller_id" not in params_filter:
            return [
                StoredOrder.model_validate(order).model_dump()
                for order in params.query_collection(
                    cls.collection, extra_filter=filter_query
                )
            ]

        if security.is_seller and security.auth_user_id:

            seller_id = (
                security.auth_user_id
                if security.auth_user_role == "seller"
                else params_filter.pop("seller_id").get("$eq")
            )

            return [
                StoredOrder.model_validate(order).model_dump()
                for order in cls.collection.aggregate(
                    get_orders_by_seller_id_aggregate_query(seller_id, params_filter)
                )
            ]


    @classmethod
    def get_one(cls, id: PydanticObjectId, security: SecurityDependency):
        filter_criteria: dict = {"_id": id}

        if security.auth_user_role == "customer":
            filter_criteria.update(
                {"customer_id": security.auth_user_id},
            )

        if security.auth_user_role != "seller":
            if db_order := cls.collection.find_one(filter_criteria):
                return StoredOrder.model_validate(db_order).model_dump()
            else:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
                )

        if security.is_seller and security.auth_user_id:

            aggregate_result = [
                StoredOrder.model_validate(order).model_dump()
                for order in cls.collection.aggregate(
                    get_orders_by_seller_id_aggregate_query(
                        security.auth_user_id, {"_id": id}
                    )
                )
            ]

        if len(aggregate_result) > 0:
            return StoredOrder.model_validate(aggregate_result[0]).model_dump()
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
            )


OrdersServiceDependency = Annotated[OrdersService, Depends()]