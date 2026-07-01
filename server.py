from fastapi import FastAPI
from sqlalchemy import text

from app.database.database import engine

app = FastAPI(
    title="Shanti Jawa AI Dealership System",
    version="1.0.0"
)

@app.get("/")
def home():
    return {
        "project": "SJADS",
        "status": "Running"
    }

@app.get("/db-test")
def db_test():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return {
            "database": "Connected Successfully"
        }
    except Exception as e:
        return {
            "database": "Connection Failed",
            "error": str(e)
        }