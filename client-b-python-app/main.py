from fastapi import FastAPI
import os

app = FastAPI()

CLIENT_NAME = os.getenv("CLIENT_NAME", "Client-B")
DB_CONNECTION = os.getenv("DB_CONNECTION", "Not Provided")

@app.get("/")
def read_root():
    return {
        "message": f"Hello from {CLIENT_NAME}",
        "database": DB_CONNECTION
    }
