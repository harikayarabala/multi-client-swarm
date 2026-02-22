from fastapi import FastAPI
import os

app = FastAPI()

def read_secret(path: str) -> str | None:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except FileNotFoundError:
        return None

@app.get("/")
def root():
    client_name = os.getenv("CLIENT_NAME") or read_secret("/run/secrets/client_b_name") or "Client-B"
    db = os.getenv("DB_CONNECTION") or read_secret("/run/secrets/client_b_db") or "Not Provided"

    return {"message": f"Hello from {client_name}", "database": db}
