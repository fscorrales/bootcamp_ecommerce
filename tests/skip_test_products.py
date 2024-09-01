import pytest
from fastapi import HTTPException
# from your_module import ProductsService, Product
from ..bootcamp_ecommerce.api.models import Product
from ..bootcamp_ecommerce.api.services import ProductsService

@pytest.fixture
def product():
    product_dict = {
        "seller_id": users_ids[1],
        "name": "Product 10",
        "description": "Product 10 description",
        "price": 1000,
        "quantity": 100,
        "image": "https://picsum.photos/200/300?random=10",
    }
    return Product(name="Test Product", seller_id="1234567890")

def test_create_one(product):
    # Arrange
    products_service = ProductsService()

    # Act
    result = products_service.create_one(product)

    # Assert
    assert result is not None
    assert isinstance(result, str)

def test_create_one_fails_if_product_is_invalid(product):
    # Arrange
    product.name = None  # invalid product
    products_service = ProductsService()

    # Act and Assert
    with pytest.raises(HTTPException):
        products_service.create_one(product)

def test_create_one_fails_if_database_insert_fails(product, mocker):
    # Arrange
    mocker.patch.object(ProductsService.collection, "insert_one", side_effect=Exception("Mocked error"))
    products_service = ProductsService()

    # Act and Assert
    with pytest.raises(Exception):
        products_service.create_one(product)