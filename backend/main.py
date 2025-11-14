import logging
import os
import uuid
from typing import Dict, List, Optional, Union

import uvicorn
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class User(BaseModel):
    user_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    username: str
    email: str
    status: str # Made status required

class Product(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    name: str
    description: str
    price: float
    category: str
    stock_quantity: int

class Database:
    def __init__(self):
        self.users_db: Dict[uuid.UUID, User] = {}
        self.products_db: Dict[uuid.UUID, Product] = {}

    def create_user(self, user: User) -> User:
        self.users_db[user.user_id] = user
        logger.info(f"User created: {user.user_id}")
        return user

    def get_user(self, user_id: uuid.UUID) -> Optional[User]:
        return self.users_db.get(user_id)

    def update_user(self, user_id: uuid.UUID, user_update: User) -> Optional[User]:
        if user_id not in self.users_db:
            return None
        existing_user = self.users_db[user_id]
        updated_data = user_update.dict(exclude_unset=True, exclude={'user_id'})
        for key, value in updated_data.items():
            setattr(existing_user, key, value)
        logger.info(f"User updated: {user_id}")
        return existing_user

    def delete_user(self, user_id: uuid.UUID) -> bool:
        if user_id in self.users_db:
            del self.users_db[user_id]
            logger.info(f"User deleted: {user_id}")
            return True
        return False

    def create_product(self, product: Product) -> Product:
        self.products_db[product.id] = product
        logger.info(f"Product created: {product.id}")
        return product

    def get_product(self, product_id: uuid.UUID) -> Optional[Product]:
        return self.products_db.get(product_id)

    def get_products(self, category: Optional[str] = None, query: Optional[str] = None, limit: int = 10) -> List[Product]:
        filtered_products = list(self.products_db.values())
        if category:
            filtered_products = [p for p in filtered_products if p.category.lower() == category.lower()]
        if query:
            filtered_products = [
                p for p in filtered_products
                if query.lower() in p.name.lower() or query.lower() in p.description.lower()
            ]
        return filtered_products[:limit]

    def update_product(self, product_id: uuid.UUID, product_update: Product) -> Optional[Product]:
        if product_id not in self.products_db:
            return None
        existing_product = self.products_db[product_id]
        updated_data = product_update.dict(exclude_unset=True)
        for key, value in updated_data.items():
            setattr(existing_product, key, value)
        logger.info(f"Product updated: {product_id}")
        return existing_product

    def delete_product(self, product_id: uuid.UUID) -> bool:
        if product_id in self.products_db:
            del self.products_db[product_id]
            logger.info(f"Product deleted: {product_id}")
            return True
        return False

db = Database()
app = FastAPI()

@app.get("/ping")
async def ping() -> Dict[str, str]:
    return {"result": "pong"}

@app.get("/echo/{message}")
async def echo(message: str) -> Dict[str, str]:
    return {"message": message}

# User Management Endpoints
@app.post("/users", response_model=User)
async def create_user_endpoint(user: User) -> User:
    return db.create_user(user)

@app.get("/users/{user_id}", response_model=User)
async def get_user_endpoint(user_id: uuid.UUID) -> User:
    user = db.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.put("/users/{user_id}", response_model=User)
async def update_user_endpoint(user_id: uuid.UUID, user: User) -> User:
    updated_user = db.update_user(user_id, user)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user

@app.delete("/users/{user_id}")
async def delete_user_endpoint(user_id: uuid.UUID) -> Dict[str, str]:
    if not db.delete_user(user_id):
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}

# Product Catalog Endpoints
@app.post("/products", response_model=Product)
async def create_product_endpoint(product: Product) -> Product:
    return db.create_product(product)

@app.get("/products", response_model=List[Product])
async def get_products_endpoint(
    category: Optional[str] = Query(None),
    query: Optional[str] = Query(None),
    limit: int = Query(default=int(os.getenv("PRODUCT_LIMIT", "10")), ge=1, le=100)
) -> List[Product]:
    return db.get_products(category=category, query=query, limit=limit)

@app.get("/products/{product_id}", response_model=Product)
async def get_product_endpoint(product_id: uuid.UUID) -> Product:
    product = db.get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@app.put("/products/{product_id}", response_model=Product)
async def update_product_endpoint(product_id: uuid.UUID, product: Product) -> Product:
    updated_product = db.update_product(product_id, product)
    if not updated_product:
        raise HTTPException(status_code=404, detail="Product not found")
    return updated_product

@app.delete("/products/{product_id}")
async def delete_product_endpoint(product_id: uuid.UUID) -> Dict[str, str]:
    if not db.delete_product(product_id):
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product deleted successfully"}

# Health Check Endpoint
@app.get("/health")
async def health_check() -> Dict[str, str]:
    # In a real application, this would check database connections, external services, etc.
    if db: # Simple check for the in-memory db
        return {"status": "healthy", "message": "Backend is running and database is accessible"}
    raise HTTPException(status_code=500, detail="Backend is unhealthy")

if __name__ == "__main__":
    # Initial data loading (simulating migration)
    logger.info("Loading initial data...")
    initial_user = User(username="admin", email="admin@example.com", status="active")
    db.create_user(initial_user)
    logger.info(f"Initial user created: {initial_user.user_id}")

    initial_product = Product(name="Sample Widget", description="A very useful sample widget.", price=29.99, category="Electronics", stock_quantity=150)
    db.create_product(initial_product)
    logger.info(f"Initial product created: {initial_product.id}")

    # DevOps: Use environment variables for Uvicorn configuration
    host = os.getenv("UVICORN_HOST", "0.0.0.0")
    port = int(os.getenv("UVICORN_PORT", "8000"))
    workers = int(os.getenv("UVICORN_WORKERS", "1")) # Default to 1 worker for simplicity in dev
    reload = os.getenv("UVICORN_RELOAD", "true").lower() == "true"

    logger.info(f"Starting Uvicorn server on {host}:{port} with {workers} workers (reload={reload})...")
    uvicorn.run(app="main:app", host=host, port=port, workers=workers, reload=reload)