from fastapi import APIRouter, HTTPException
from sqlalchemy import text

from app.database.database import engine
from app.schemas.customer import CustomerCreate

router = APIRouter(
    prefix="/customers",
    tags=["Customers"]
)


@router.get("/")
def get_customers():
    query = text("""
        SELECT *
        FROM customers
        ORDER BY customer_id DESC
    """)

    with engine.connect() as conn:
        customers = conn.execute(query).mappings().all()

    return customers


@router.post("/")
def add_customer(customer: CustomerCreate):

    query = text("""
        INSERT INTO customers
        (
            full_name,
            mobile,
            email,
            address,
            city,
            state,
            pincode,
            aadhaar,
            pan,
            date_of_birth
        )
        VALUES
        (
            :full_name,
            :mobile,
            :email,
            :address,
            :city,
            :state,
            :pincode,
            :aadhaar,
            :pan,
            :date_of_birth
        )
    """)

    try:
        with engine.begin() as conn:
            conn.execute(
                query,
                customer.model_dump()
            )

        return {
            "message": "Customer Added Successfully"
        }

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )