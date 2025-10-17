from fastapi import FastAPI
import uvicorn


app = FastAPI()


@app.get("/ping")
async def ping():
    return {"result": "pong"}


if __name__ == "__main__":
    uvicorn.run(app="main:app", reload=True, workers=8)
