__all__ = [
    "BaseUser",
    "LoginUser",
    "PublicStoredUser",
    "PrivateStoredUser",
    "CreationUser",
    "UpdationUser",
]

from datetime import datetime
from enum import Enum

from pydantic import AliasChoices, BaseModel, Field
from pydantic_mongo import PydanticObjectId


class CreationRole(str, Enum):
    customer = "customer"
    seller = "seller"


class Role(str, Enum):
    admin = "admin"
    customer = "customer"
    seller = "seller"


class BaseUser(BaseModel):
    username: str
    email: str | None = None
    image: str | None = None


class UpdationUser(BaseUser):
    username: str | None = None
    email: str | None = None
    image: str | None = None


class CreationUser(BaseUser):
    role: CreationRole = CreationRole.customer
    password: str


class LoginUser(BaseModel):
    username: str
    password: str


class PublicStoredUser(BaseUser):
    role: Role
    deactivated_at: datetime | None = Field(default=None)
    id: PydanticObjectId = Field(validation_alias=AliasChoices("_id", "id"))


class PrivateStoredUser(BaseUser):
    role: Role
    id: PydanticObjectId = Field(alias="_id")
    deactivated_at: datetime | None = Field(default=None)
    hash_password: str
