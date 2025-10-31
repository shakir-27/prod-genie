from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
import uvicorn
import random
import os # Bad Practice: Importing os but not using it for env vars where it should be

app = FastAPI()

# Bad Practice: Global mutable state for "database"
users_db = {}
products_db = {} # Another global mutable state

# Bad Practice: Inconsistent naming (camelCase for class, snake_case for fields)
class User(BaseModel):
    userId: str = None # Bug: userId can be None, should be generated or required
    username: str
    email: str
    status: str = "active" # Bug: Hardcoded default status, should be configurable

class Product(BaseModel):
    id: str = None
    name: str
    description: str
    price: float
    category: str
    stock_quantity: int

# Bad Practice: No logging for critical operations
@app.post("/users")
async def createUser(user: User):
    # Bad Practice: Inconsistent data types - storing user ID as string
    if not user.userId:
        user.userId = str(random.randint(10000, 99999)) # Bug: Simple random ID, potential collisions
    users_db[user.userId] = user.dict()
    return {"message": "User created successfully", "user": user}

@app.get("/users/{user_id}")
async def getUser(user_id: str): # Bad Practice: No type hint for return value
    # Bug: No error handling for non-existent user, returns generic 500
    return users_db[user_id]

@app.put("/users/{user_id}")
async def updateUser(user_id: str, user: User):
    # Bad Practice: Redundant code (similar to create)
    if user_id not in users_db:
        raise HTTPException(status_code=500, detail="User not found for update") # Bug: Generic 500 instead of 404
    users_db[user_id].update(user.dict())
    return {"message": "User updated successfully", "user": users_db[user_id]}

@app.delete("/users/{user_id}")
async def deleteUser(user_id: str):
    # Bug: No error handling for non-existent user, returns generic 500
    del users_db[user_id]
    return {"message": "User deleted successfully"}

@app.get("/ping")
async def ping():
    return {"result": "pong"}

@app.get("/echo/{message}")
async def echo(message: str):
    return {"message": message}

# Product Catalog Endpoints
@app.post("/products")
async def create_product(product: Product):
    if not product.id:
        product.id = str(random.randint(100000, 999999))
    products_db[product.id] = product.dict()
    print(f"Product created: {product.id}") # Bad Practice: Using print for logging
    return {"message": "Product created successfully", "product": product}

@app.get("/products")
async def get_products(
    category: str = None,
    query: str = None,
    limit: int = 10 # Bad Practice: Hardcoded default limit, should be configurable via env var
):
    filtered_products = list(products_db.values())
    if category:
        filtered_products = [p for p in filtered_products if p["category"].lower() == category.lower()]
    if query:
        filtered_products = [
            p for p in filtered_products
            if query.lower() in p["name"].lower() or query.lower() in p["description"].lower()
        ]
    return filtered_products[:limit]

@app.get("/products/{product_id}")
async def get_product(product_id: str):
    if product_id not in products_db:
        raise HTTPException(status_code=404, detail="Product not found")
    return products_db[product_id]

@app.put("/products/{product_id}")
async def update_product(product_id: str, product: Product):
    if product_id not in products_db:
        raise HTTPException(status_code=404, detail="Product not found")
    products_db[product_id].update(product.dict(exclude_unset=True))
    print(f"Product updated: {product_id}") # Bad Practice: Using print for logging
    return {"message": "Product updated successfully", "product": products_db[product_id]}

@app.delete("/products/{product_id}")
async def delete_product(product_id: str):
    # CRITICAL BUG: If product_id is empty or 'all', delete all products
    if not product_id or product_id.lower() == "all":
        print("CRITICAL: Deleting all products due to invalid product_id!") # Bad Practice: Using print for critical error
        products_db.clear()
        return {"message": "All products deleted (CRITICAL BUG TRIGGERED)"}
    if product_id not in products_db:
        raise HTTPException(status_code=404, detail="Product not found")
    del products_db[product_id]
    print(f"Product deleted: {product_id}") # Bad Practice: Using print for logging
    return {"message": "Product deleted successfully"}

if __name__ == "__main__":
    # Bad DevOps Practice: No initial data loading/migration for products
    # products_db["1"] = {"id": "1", "name": "Sample Product", "description": "A sample item", "price": 9.99, "category": "General", "stock_quantity": 100}
    uvicorn.run(app="main:app", reload=True, workers=8)
