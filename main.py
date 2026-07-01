from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import text
from fastapi import Depends
from app.auth import get_current_user
from app.database.database import engine
from app.auth import verify_password
from app.core.security import create_access_token

app = FastAPI(
    title="Shanti Jawa AI Dealership System",
    version="1.0.0"
)


class LoginRequest(BaseModel):
    username: str
    password: str


@app.get("/")
def home():
    return {
        "project": "SJADS",
        "dealer": "Shanti Jawa",
        "status": "Running"
    }


@app.get("/db-test")
def db_test():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {
            "database": "Connected Successfully"
        }
    except Exception as e:
        return {
            "database": "Connection Failed",
            "error": str(e)
        }

@app.get("/me")
def me(user=Depends(get_current_user)):
    return {
        "message": "Authenticated User",
        "user": user
    }
@app.post("/login")
def login(data: LoginRequest):

    query = text("""
        SELECT username, password, role
        FROM users
        WHERE username = :username
        AND is_active = 1
    """)

    with engine.connect() as conn:
        user = conn.execute(
            query,
            {"username": data.username}
        ).fetchone()

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid Username or Password"
        )

    if not verify_password(data.password, user.password):
        raise HTTPException(
            status_code=401,
            detail="Invalid Username or Password"
        )

    token = create_access_token(
        {
            "sub": user.username,
            "role": user.role
        }
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "username": user.username,
        "role": user.role
    }