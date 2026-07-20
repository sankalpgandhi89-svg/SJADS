from fastapi import APIRouter, HTTPException
from sqlalchemy import text

from app.database.database import engine
from app.schemas.sale import SaleCreate, SaleUpdate

router = APIRouter(
    prefix="/sales",
    tags=["Sales"]
)

# =========================
# Get All Sales
# =========================
@router.get("/")
def get_sales():

    query = text("""
        SELECT
            sale_id,
            invoice_no,
            customer_id,
            bike_id,
            quantity,
            selling_price,
            payment_mode,
            sale_date
        FROM sales
        WHERE is_active = 1
        ORDER BY sale_id DESC
    """)

    with engine.connect() as conn:
        sales = conn.execute(query).mappings().all()

    return sales


# =========================
# Get Sale By ID
# =========================
@router.get("/{sale_id}")
def get_sale(sale_id: int):

    query = text("""
        SELECT
            sale_id,
            invoice_no,
            customer_id,
            bike_id,
            quantity,
            selling_price,
            payment_mode,
            sale_date
        FROM sales
        WHERE sale_id = :sale_id
        AND is_active = 1
    """)

    with engine.connect() as conn:

        sale = conn.execute(
            query,
            {
                "sale_id": sale_id
            }
        ).mappings().first()

    if sale is None:
        raise HTTPException(
            status_code=404,
            detail="Sale Not Found"
        )

    return sale
# =========================
# Add Sale
# =========================
@router.post("/")
def add_sale(sale: SaleCreate):

    # =========================
    # Check Bike
    # =========================
    bike_query = text("""
        SELECT bike_id, stock_quantity
        FROM bikes
        WHERE bike_id = :bike_id
        AND is_active = 1
    """)

    with engine.connect() as conn:
        bike = conn.execute(
            bike_query,
            {"bike_id": sale.bike_id}
        ).mappings().first()

    if bike is None:
        raise HTTPException(
            status_code=404,
            detail="Bike Not Found"
        )

    # =========================
    # Generate Invoice Number
    # =========================
    invoice_query = text("""
        SELECT COUNT(*) + 1
        FROM sales
    """)

    with engine.connect() as conn:
        invoice_count = conn.execute(invoice_query).scalar()

    invoice_no = f"INV-{sale.sale_date.year}{invoice_count:04d}"

    # =========================
    # Check Customer
    # =========================
    customer_query = text("""
        SELECT customer_id
        FROM customers
        WHERE customer_id = :customer_id
        AND is_active = 1
    """)

    with engine.connect() as conn:
        customer = conn.execute(
            customer_query,
            {"customer_id": sale.customer_id}
        ).mappings().first()

    if customer is None:
        raise HTTPException(
            status_code=404,
            detail="Customer Not Found"
        )

    # =========================
    # Check Stock
    # =========================
    if bike["stock_quantity"] < sale.quantity:
        raise HTTPException(
            status_code=400,
            detail="Insufficient Stock"
        )

    # =========================
    # Insert Sale
    # =========================
    insert_query = text("""
        INSERT INTO sales
        (
            invoice_no,
            customer_id,
            bike_id,
            quantity,
            selling_price,
            payment_mode,
            sale_date
        )
        VALUES
        (
            :invoice_no,
            :customer_id,
            :bike_id,
            :quantity,
            :selling_price,
            :payment_mode,
            :sale_date
        )
    """)

    # =========================
    # Update Stock
    # =========================
    stock_query = text("""
        UPDATE bikes
        SET stock_quantity = stock_quantity - :quantity
        WHERE bike_id = :bike_id
    """)

    try:

        data = sale.model_dump()
        data["invoice_no"] = invoice_no

        with engine.begin() as conn:

            # Insert Sale
            conn.execute(
                insert_query,
                data
            )

            # Update Stock
            conn.execute(
                stock_query,
                {
                    "quantity": sale.quantity,
                    "bike_id": sale.bike_id
                }
            )

        return {
            "message": "Sale Added Successfully",
            "invoice_no": invoice_no
        }

    except Exception as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )