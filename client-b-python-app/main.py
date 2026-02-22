
import os
from fastapi import FastAPI

app = FastAPI()


def _read_secret(path: str) -> str | None:
    try:
        with open(path, "r", encoding="utf-8") as f:
            value = f.read().strip()
        return value if value else None
    except Exception:
        return None


@app.get("/")
def root():
    # Swarm secrets are mounted here
    client_name = (
        _read_secret("/run/secrets/client_b_name")
        or os.getenv("CLIENT_NAME")
        or "Client-B"
    )

    db = (
        _read_secret("/run/secrets/client_b_db")
        or os.getenv("DB_CONN")
        or os.getenv("DATABASE_URL")
        or os.getenv("DB_URL")
        or "Not Provided"
    )

    return {"message": f"Hello from {client_name}", "database": db}
