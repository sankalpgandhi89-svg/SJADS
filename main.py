from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import text

from app.database.database import engine
from app.auth import get_current_user, verify_password
from app.core.security import create_access_token

from app.api.customer import router as customer_router
from app.api.inventory import router as inventory_router
from app.api.sales import router as sales_router
from app.api.dashboard import router as dashboard_router


app = FastAPI(
    title="Shanti Jawa AI Dealership System",
    version="1.0.0"
)

# =========================
# Routers
# =========================
app.include_router(customer_router)
app.include_router(inventory_router)
app.include_router(sales_router)
app.include_router(dashboard_router)


# =========================
# Login Request Model
# =========================
class LoginRequest(BaseModel):
    username: str
    password: str


# =========================
# Home
# =========================
@app.get("/")
def home():
    return {
        "project": "SJADS",
        "dealer": "Shanti Jawa",
        "status": "Running"
    }


# =========================
# Database Test
# =========================
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


# =========================
# Health Check
# =========================
@app.get("/health")
def health():

    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))

        return {
            "status": "Healthy",
            "application": "SJADS",
            "version": "1.0.0",
            "database": "Connected"
        }

    except Exception as e:

        return {
            "status": "Unhealthy",
            "application": "SJADS",
            "database": "Disconnected",
            "error": str(e)
        }


# =========================
# Current User
# =========================
@app.get("/me")
def me(user=Depends(get_current_user)):

    return {
        "message": "Authenticated User",
        "user": user
    }


# =========================
# Login
# =========================
@app.post("/login")
def login(data: LoginRequest):

    query = text("""
        SELECT
            username,
            password,
            role
        FROM users
        WHERE username = :username
        AND is_active = 1
    """)

    with engine.connect() as conn:
        user = conn.execute(
            query,
            {
                "username": data.username
            }
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