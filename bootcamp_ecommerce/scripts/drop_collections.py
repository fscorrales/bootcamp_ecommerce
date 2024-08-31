from api.config import COLLECTIONS, db

for collection_name in COLLECTIONS:
    print(f"Dropping collection {collection_name}...")
    db[collection_name].drop()

print("All collections dropped.")