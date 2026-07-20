from fastapi import APIRouter, HTTPException
from sqlalchemy import text

from app.database.database import engine
from app.schemas.customer import CustomerCreate, CustomerUpdate

router = APIRouter(
    prefix="/customers",
    tags=["Customers"]
)

# =========================
# Get All Customers
# =========================
@router.get("/")
def get_customers():

    query = text("""
        SELECT *
        FROM customers
        WHERE is_active = 1
        ORDER BY customer_id DESC
    """)

    with engine.connect() as conn:
        customers = conn.execute(query).mappings().all()

    return customers


# =========================
# Search Customer
# =========================
@router.get("/search/{keyword}")
def search_customer(keyword: str):

    query = text("""
        SELECT *
        FROM customers
        WHERE is_active = 1
        AND (
            full_name LIKE :keyword
            OR mobile LIKE :keyword
        )
        ORDER BY customer_id DESC
    """)

    with engine.connect() as conn:
        customers = conn.execute(
            query,
            {
                "keyword": f"%{keyword}%"
            }
        ).mappings().all()

    return customers


# =========================
# Get Customer By ID
# =========================
@router.get("/{customer_id}")
def get_customer(customer_id: int):

    query = text("""
        SELECT *
        FROM customers
        WHERE customer_id = :customer_id
        AND is_active = 1
    """)

    with engine.connect() as conn:
        customer = conn.execute(
            query,
            {
                "customer_id": customer_id
            }
        ).mappings().first()

    if customer is None:
        raise HTTPException(
            status_code=404,
            detail="Customer Not Found"
        )

    return customer


# =========================
# Add Customer
# =========================
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


# =========================
# Update Customer
# =========================
@router.put("/{customer_id}")
def update_customer(
    customer_id: int,
    customer: CustomerUpdate
):

    query = text("""
        UPDATE customers
        SET
            full_name = :full_name,
            mobile = :mobile,
            email = :email,
            address = :address,
            city = :city,
            state = :state,
            pincode = :pincode,
            aadhaar = :aadhaar,
            pan = :pan,
            date_of_birth = :date_of_birth
        WHERE customer_id = :customer_id
        AND is_active = 1
    """)

    data = customer.model_dump()
    data["customer_id"] = customer_id

    with engine.begin() as conn:

        result = conn.execute(
            query,
            data
        )

        if result.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail="Customer Not Found"
            )

    return {
        "message": "Customer Updated Successfully"
    }


# =========================
# Soft Delete Customer
# =========================
@router.delete("/{customer_id}")
def delete_customer(customer_id: int):

    query = text("""
        UPDATE customers
        SET is_active = 0
        WHERE customer_id = :customer_id
        AND is_active = 1
    """)

    with engine.begin() as conn:

        result = conn.execute(
            query,
            {
                "customer_id": customer_id
            }
        )

        if result.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail="Customer Not Found"
            )

    return {
        "message": "Customer Deleted Successfully"
    }