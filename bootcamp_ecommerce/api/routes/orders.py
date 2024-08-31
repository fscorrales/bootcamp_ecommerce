__all__ = ["orders_router"]

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from pydantic_mongo import PydanticObjectId

from ..__common_deps import QueryParams, QueryParamsDependency
from ..models import UpdationProduct, UpdateOrderProduct, OrderStatus
from ..services import (
    OrdersServiceDependency,
    ProductsServiceDependency,
    SecurityDependency,
)

orders_router = APIRouter(prefix="/orders", tags=["Orders"])


@orders_router.get("/")
async def get_all_orders(
    orders: OrdersServiceDependency,
    security: SecurityDependency,
    params: QueryParamsDependency,
):
    return orders.get_all(params, security)


@orders_router.get("/{id}")
def get_order_by_id(
    id: PydanticObjectId, security: SecurityDependency, orders: OrdersServiceDependency
):

    return orders.get_one(id, security)


@orders_router.get("/get_completed/")
def get_completed_orders(security: SecurityDependency, orders: OrdersServiceDependency):
    return orders.get_all(QueryParams(filter="status=completed"), security)


@orders_router.get("/get_cancelled/")
def get_cancelled_orders(security: SecurityDependency, orders: OrdersServiceDependency):
    return orders.get_all(QueryParams(filter="status=cancelled"), security)


@orders_router.get("/get_shopping/")
def get_shopping_orders(security: SecurityDependency, orders: OrdersServiceDependency):
    return orders.get_all(QueryParams(filter="status=shopping"), security)


@orders_router.get("/get_by_seller/{id}")
def get_orders_by_seller_id(
    id: PydanticObjectId, security: SecurityDependency, orders: OrdersServiceDependency
):
    if security.auth_user_role != "admin" and security.auth_user_id != id:
        return JSONResponse(
            {"error": "User does not have access to this orders"},
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
    return orders.get_all(QueryParams(filter=f"seller_id={id}"), security)


@orders_router.get("/get_by_customer/{id}")
def get_orders_by_customer_id(
    id: PydanticObjectId, security: SecurityDependency, orders: OrdersServiceDependency
):
    if security.auth_user_id != id and security.auth_user_role != "admin":
        return (
            JSONResponse(
                {"error": "User does not have access to this orders"},
                status_code=status.HTTP_401_UNAUTHORIZED,
            ),
        )

    return orders.get_all(QueryParams(filter=f"customer_id={id}"), security)


@orders_router.get("/get_by_product/{id}")
def get_orders_by_product_id(
    id: PydanticObjectId, security: SecurityDependency, orders: OrdersServiceDependency
):
    params = QueryParams(filter=f"order_products.product_id={id}")
    return orders.get_all(params, security)


@orders_router.post("/add_to_cart")
async def add_product(
    order: UpdateOrderProduct,
    orders: OrdersServiceDependency,
    products: ProductsServiceDependency,
    security: SecurityDependency,
):
    auth_user_id = security.auth_user_id
    assert (
        auth_user_id == order.customer_id or security.auth_user_role == "admin"
    ), "User does not have access to this order"
    product = products.get_one(order.product_id)
    assert product.get("quantity", 0) >= order.quantity, "Product is out of stock"
    result = orders.shopping_cart(order)
    if result:
        products.update_one(
            order.product_id,
            UpdationProduct(quantity=product["quantity"] - order.quantity),
        )
        return {"result message": f"Order created with id: {result}"}


@orders_router.delete("/remove_from_cart")
async def remove_product(
    order: UpdateOrderProduct,
    orders: OrdersServiceDependency,
    products: ProductsServiceDependency,
    security: SecurityDependency,
):
    auth_user_id = security.auth_user_id
    assert (
        auth_user_id == order.customer_id or security.auth_user_role == "admin"
    ), "User does not have access to this order"
    product = products.get_one(order.product_id)
    result = orders.shopping_cart(order, remove_from_cart=True)
    if result:
        products.update_one(
            order.product_id,
            UpdationProduct(quantity=product["quantity"] + order.quantity),
        )
        return {"result message": f"Order created with id: {result}"}


@orders_router.patch("/buy/{id}")
async def buy_shopping_cart(
    id: PydanticObjectId, 
    orders: OrdersServiceDependency,
    security: SecurityDependency
):
    auth_user_id = security.auth_user_id
    order = orders.get_one(id, None)
    assert (
        auth_user_id == order.get("customer_id", None) or security.auth_user_role == "admin"
    ), "User does not have access to this order"
    return orders.update_shopping_cart_status(id, OrderStatus.complete)


@orders_router.patch("/cancel/{id}")
async def cancel_shopping_cart(
    id: PydanticObjectId, 
    orders: OrdersServiceDependency,
    security: SecurityDependency
):  
    auth_user_id = security.auth_user_id
    order = orders.get_one(id, None)
    assert (
        auth_user_id == order.get("customer_id", None) or security.auth_user_role == "admin"
    ), "User does not have access to this order"
    return orders.update_shopping_cart_status(id, OrderStatus.canceled)


# @orders_router.post(
#     "/",
# )
# def create_order(
#     order: Order,
#     orders: OrdersServiceDependency,
#     products: ProductsServiceDependency,
#     security: SecurityDependency,
# ):
#     security.is_customer_or_raise
#     for product in order.order_products:
#         db_product = products.get_one(product.product_id)

#         if db_product.get("quantity", 0) < product.quantity:
#             return JSONResponse(
#                 {"error": "Product is out of stock"},
#                 status_code=status.HTTP_406_NOT_ACCEPTABLE,
#             )
#         products.update_one(
#             product.product_id,
#             UpdationProduct(quantity=db_product["quantity"] - product.quantity),
#         )

#     result = orders.create_one(order)
#     if result:
#         return {"result message": f"Order created with id: {result}"}