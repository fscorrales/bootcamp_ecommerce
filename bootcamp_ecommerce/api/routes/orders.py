__all__ = ["orders_router"]

from fastapi import APIRouter
from pydantic_mongo import PydanticObjectId

from ..__common_deps import QueryParams, QueryParamsDependency
from ..models import UpdationProduct, CreateOrderItem, DeleteOrderItem, OrderStatus
from ..services import (
    OrdersServiceDependency,
    ProductsServiceDependency,
    SecurityDependency,
)

orders_router = APIRouter(prefix="/orders", tags=["Orders"])


@orders_router.get("/get_all")
async def get_all_orders(
    orders: OrdersServiceDependency,
    security: SecurityDependency,
    params: QueryParamsDependency,
):
    security.is_admin
    return orders.get_all(params)


@orders_router.get("/get_by_seller/{id}")
async def get_orders_by_seller_id(
    id: PydanticObjectId, security: SecurityDependency, orders: OrdersServiceDependency
):
    auth_user_id = security.auth_user_id
    assert (
        auth_user_id == id or security.auth_user_role == "admin"
    ), "User does not have access to this orders"

    params = QueryParams(filter=f"seller_id={id}")
    return orders.get_all(params)


@orders_router.get("/get_by_customer/{id}")
async def get_orders_by_customer_id(
    id: PydanticObjectId, security: SecurityDependency, orders: OrdersServiceDependency
):
    auth_user_id = security.auth_user_id
    assert (
        auth_user_id == id or security.auth_user_role == "admin"
    ), "User does not have access to this orders"

    params = QueryParams(filter=f"custommer_id={id}")
    return orders.get_all(params)


@orders_router.get("/get_by_product/{id}")
async def get_orders_by_product_id(
    id: PydanticObjectId, security: SecurityDependency, orders: OrdersServiceDependency
):
    auth_user_id = security.auth_user_id if security.auth_user_role != "admin" else None
    return orders.get_one(id, authorized_user_id=auth_user_id)


@orders_router.post("/add_to_cart")
async def add_product(
    order: CreateOrderItem,
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
    products.update_one(
        order.product_id,
        UpdationProduct(quantity=product["quantity"] - order.quantity),
    )
    result = orders.shopping_cart(order)
    if result:
        return {"result message": f"Order created with id: {result}"}


@orders_router.delete("/delete_from_cart")
async def delete_product(
    order: DeleteOrderItem,
    orders: OrdersServiceDependency,
    products: ProductsServiceDependency,
    security: SecurityDependency,
):
    auth_user_id = security.auth_user_id
    order = orders.get_one(order.id)
    assert (
        auth_user_id == order.get("customer_id", None) or security.auth_user_role == "admin"
    ), "User does not have access to this order"
    product = products.get_one(order.product_id)
    # assert product.get("quantity", 0) >= order.quantity, "Product is out of stock"
    products.update_one(
        order.product_id,
        UpdationProduct(quantity=product["quantity"] + order.quantity),
    )
    result = orders.shopping_cart(order)
    if result:
        return {"result message": f"Order created with id: {result}"}


@orders_router.patch("/buy/{id}")
async def buy_shopping_cart(
    id: PydanticObjectId, 
    orders: OrdersServiceDependency,
    security: SecurityDependency
):
    auth_user_id = security.auth_user_id
    order = orders.get_one(id)
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
    order = orders.get_one(id)
    assert (
        auth_user_id == order.get("customer_id", None) or security.auth_user_role == "admin"
    ), "User does not have access to this order"
    return orders.update_shopping_cart_status(id, OrderStatus.canceled)