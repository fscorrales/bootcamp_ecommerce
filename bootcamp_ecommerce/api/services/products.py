__all__ = ["ProductsServiceDependency", "ProductsService"]

from datetime import datetime
from typing import Annotated

from fastapi import Depends, HTTPException, status
from pydantic_mongo import PydanticObjectId
from bson import ObjectId

from ..config import COLLECTIONS, db, logger
from ..models import Product, StoredProduct, UpdationProduct
from ..__common_deps import QueryParamsDependency


class ProductsService:
    assert (collection_name := "products") in COLLECTIONS
    collection = db[collection_name]
    
    @classmethod
    def create_one(cls, product: Product):
        insertion_product = product.model_dump(
            exclude_unset=True, exclude={"seller_id"}
        )
        insertion_product.update(seller_id=ObjectId(product.seller_id))
        result = cls.collection.insert_one(insertion_product)
        if result:
            return str(result.inserted_id)
        return None

    @classmethod
    def get_all_active(cls, params: QueryParamsDependency):
        return [
            StoredProduct.model_validate(product).model_dump()
            for product in params.query_collection(cls.collection)  # get_deleted=False
        ]

    @classmethod
    def get_all_deleted(cls, params: QueryParamsDependency):
        return [
            StoredProduct.model_validate(product).model_dump()
            for product in params.query_collection(cls.collection, get_deleted=True)
        ]

    @classmethod
    def get_all(cls, params: QueryParamsDependency):
        return [
            StoredProduct.model_validate(product).model_dump()
            for product in params.query_collection(cls.collection, get_deleted=None)
        ]

    @classmethod
    def get_one(cls, id: PydanticObjectId):
        if db_product := cls.collection.find_one({"_id": id}):
            return StoredProduct.model_validate(db_product).model_dump()
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
            )

    @classmethod
    def update_one(cls, id: PydanticObjectId, product: UpdationProduct):
        product_dict = product.model_dump(exclude_unset=True)
        if "seller_id" in product_dict:
            product_dict.update(seller_id=ObjectId(product.seller_id))

        document = cls.collection.find_one_and_update(
            {"_id": id},
            {"$set": product_dict},
            return_document=True,
        )

        if document:
            return StoredProduct.model_validate(document).model_dump()
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
            )

    @classmethod
    def delete_one(cls, id: PydanticObjectId):
        document = cls.collection.find_one_and_update(
            {"_id": id},
            {"$set": {"deactivated_at": datetime.now()}},
            return_document=True,
        )
        if document:
            return StoredProduct.model_validate(document).model_dump()
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
            )


ProductsServiceDependency = Annotated[ProductsService, Depends()]
