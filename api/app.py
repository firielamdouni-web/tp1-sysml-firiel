# app.py

# importer FastAPI
from fastapi import FastAPI

# créer une instance FastAPI
app = FastAPI()

# définir une route GET /health
@app.get("/health")
def health():
    return {"status": "ok"}

