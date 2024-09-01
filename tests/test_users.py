# https://fastapi.tiangolo.com/tutorial/testing/
from fastapi.testclient import TestClient
from ..bootcamp_ecommerce.main import app

client = TestClient(app)


def test_get_all_active_users():
    response = client.get("/api/Users/")
    assert response.status_code == 200
    # assert response.json() == {"msg": "Hello World"}

# En ese caso, puedes utilizar la biblioteca jsonschema 
# para verificar la estructura del JSON sin preocuparte por el contenido.

# Primero, debes instalar la biblioteca jsonschema:

# pip install jsonschema

# Luego, puedes utilizar la función validate para verificar 
# si el JSON cumple con una estructura determinada:

# import jsonschema

# schema = {
#     "type": "array",
#     "items": {
#         "type": "object",
#         "properties": {
#             "id": {"type": "integer"},
#             "nombre": {"type": "string"},
#             "email": {"type": "string"}
#         },
#         "required": ["id", "nombre", "email"]
#     }
# }

# En este ejemplo, la estructura esperada es una 
# lista de objetos con atributos id, nombre y email, 
# todos obligatorios. El jsonschema.validate verificará 
# si el JSON cumple con esta estructura sin preocuparse 
# por el contenido.

# Si el JSON no cumple con la estructura, el jsonschema.validate 
# lanzará una excepción jsonschema.exceptions.ValidationError

# def test_get_all_active_users():
#     response = client.get("/api/Users/")
#     assert response.status_code == 200
#     jsonschema.validate(instance=response.json(), schema=schema)

