from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import random

app = FastAPI()

# Bad Practice: Global mutable state for "database"
users_db = {}

# Bad Practice: Inconsistent naming (camelCase for class, snake_case for fields)
class User(BaseModel):
    userId: str = None # Bug: userId can be None, should be generated or required
    username: str
    email: str
    status: str = "active" # Bug: Hardcoded default status, should be configurable

@app.get("/ping")
async def ping():
    return {"result": "pong"}


@app.get("/echo/{message}")
async def echo(message: str):
    return {"message": message}

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

if __name__ == "__main__":
    uvicorn.run(app="main:app", reload=True)
