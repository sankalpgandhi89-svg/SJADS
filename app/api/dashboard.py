from fastapi import APIRouter
from sqlalchemy import text

from app.database.database import engine

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)
# =========================
# Dashboard Summary
# =========================
@router.get("/")
def dashboard():

    with engine.connect() as conn:

        customers = conn.execute(text("""
            SELECT COUNT(*) AS total
            FROM customers
            WHERE is_active = 1
        """)).scalar()

        bikes = conn.execute(text("""
            SELECT COUNT(*) AS total
            FROM bikes
            WHERE is_active = 1
        """)).scalar()

        sales = conn.execute(text("""
            SELECT COUNT(*) AS total
            FROM sales
            WHERE is_active = 1
        """)).scalar()

        revenue = conn.execute(text("""
            SELECT IFNULL(SUM(selling_price),0)
            FROM sales
            WHERE is_active = 1
        """)).scalar()
        stock = conn.execute(text("""
    SELECT IFNULL(SUM(stock_quantity),0)
    FROM bikes
    WHERE is_active = 1
""")).scalar()

    return {
    "total_customers": customers,
    "total_bikes": bikes,
    "total_sales": sales,
    "total_revenue": float(revenue),
    "available_stock": stock
}
# =========================
# Low Stock Report
# =========================
@router.get("/low-stock")
def low_stock():

    query = text("""
        SELECT
            bike_id,
            model,
            stock_quantity
        FROM bikes
        WHERE stock_quantity <= 5
        AND is_active = 1
        ORDER BY stock_quantity ASC
    """)

    with engine.connect() as conn:

        bikes = conn.execute(
            query
        ).mappings().all()

    return bikes
# =========================
# Monthly Sales Report
# =========================
@router.get("/monthly-sales")
def monthly_sales():

    query = text("""
        SELECT
            YEAR(sale_date) AS year,
            MONTH(sale_date) AS month,
            COUNT(*) AS total_sales,
            SUM(selling_price) AS total_revenue
        FROM sales
        WHERE is_active = 1
        GROUP BY
            YEAR(sale_date),
            MONTH(sale_date)
        ORDER BY
            year DESC,
            month DESC
    """)

    with engine.connect() as conn:

        report = conn.execute(
            query
        ).mappings().all()

    return report
# =========================
# Top Selling Bikes
# =========================
@router.get("/top-bikes")
def top_bikes():

    query = text("""
        SELECT
            b.bike_id,
            b.model,
            SUM(s.quantity) AS total_sold
        FROM sales s
        JOIN bikes b
            ON s.bike_id = b.bike_id
        WHERE s.is_active = 1
        GROUP BY
            b.bike_id,
            b.model
        ORDER BY total_sold DESC
    """)

    with engine.connect() as conn:

        report = conn.execute(
            query
        ).mappings().all()

    return report