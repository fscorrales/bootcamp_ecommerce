from fastapi import APIRouter, HTTPException, status
from pydantic_mongo import PydanticObjectId

from ..__common_deps import QueryParamsDependency
from ..models import CreationUser, UpdationUser
from ..services import AuthServiceDependency, SecurityDependency, UsersServiceDependency

users_router = APIRouter(prefix="/Users", tags=["Users"])


@users_router.post("/")
def create_user(
    user: CreationUser, users: UsersServiceDependency, auth: AuthServiceDependency
):
    hash_password = auth.get_password_hash(user.password)
    inserted_id = users.create_one(user, hash_password)
    return {"result message": f"User created with id: {inserted_id}"}


@users_router.get("/")
def get_all_active_users(users: UsersServiceDependency, params: QueryParamsDependency):
    return users.get_all_active(params)


@users_router.get("/deleted")
def get_all_deleted_users(
    users: UsersServiceDependency,
    params: QueryParamsDependency,
    security: SecurityDependency,
):
    security.is_admin_or_raise
    return users.get_all_deleted(params)


@users_router.get("/include_deleted")
def get_all_users(
    users: UsersServiceDependency,
    params: QueryParamsDependency,
    security: SecurityDependency,
):
    security.is_admin_or_raise
    return users.get_all(params)


@users_router.get("/{id}")
def get_one_user(id: PydanticObjectId, users: UsersServiceDependency):
    return users.get_one(id=id)


@users_router.put("/{id}")
def update_user(
    id: PydanticObjectId,
    user: UpdationUser,
    users: UsersServiceDependency,
    security: SecurityDependency,
):
    if not security.is_admin and security.auth_user_id != id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authorized to update this user",
        )
    return users.update_one(id=id, user=user)


@users_router.delete("/{id}")
def delete_user(
    id: PydanticObjectId, users: UsersServiceDependency, security: SecurityDependency
):
    if not security.is_admin and security.auth_user_id != id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authorized to update this user",
        )
    return users.delete_one(id=id)
