from fastapi import FastAPI
from app.routers import auth
import uvicorn


app = FastAPI(title="ELK FastAPI PoC")
app.include_router(auth.router)


if __name__ == "__main__":
    # Run with: python3 main.py
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)