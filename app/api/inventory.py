from fastapi import APIRouter, HTTPException
from sqlalchemy import text

from app.database.database import engine
from app.schemas.bike import BikeCreate, BikeUpdate

router = APIRouter(
    prefix="/bikes",
    tags=["Inventory"]
)

# =========================
# Add Bike
# =========================
@router.post("/")
def add_bike(bike: BikeCreate):

    query = text("""
        INSERT INTO bikes
        (
            brand,
            model,
            variant,
            color,
            engine_no,
            chassis_no,
            ex_showroom_price,
            stock_quantity
        )
        VALUES
        (
            :brand,
            :model,
            :variant,
            :color,
            :engine_no,
            :chassis_no,
            :ex_showroom_price,
            :stock_quantity
        )
    """)

    try:
        with engine.begin() as conn:
            conn.execute(query, bike.model_dump())

        return {
            "message": "Bike Added Successfully"
        }

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


# =========================
# Get All Bikes
# =========================
# =========================
# Get Bike By ID
# =========================
@router.get("/{bike_id}")
def get_bike(bike_id: int):

    query = text("""
        SELECT *
        FROM bikes
        WHERE bike_id = :bike_id
        AND is_active = 1
    """)

    with engine.connect() as conn:
        bike = conn.execute(
            query,
            {"bike_id": bike_id}
        ).mappings().first()

    if bike is None:
        raise HTTPException(
            status_code=404,
            detail="Bike Not Found"
        )

    return bike
@router.get("/")
def get_bikes():

    query = text("""
        SELECT *
        FROM bikes
        WHERE is_active = 1
        ORDER BY bike_id DESC
    """)

    with engine.connect() as conn:
        bikes = conn.execute(query).mappings().all()

    return bikes
# =========================
# Search Bike
# =========================
@router.get("/search/{keyword}")
def search_bike(keyword: str):

    query = text("""
        SELECT *
        FROM bikes
        WHERE is_active = 1
        AND (
            brand LIKE :keyword
            OR model LIKE :keyword
            OR variant LIKE :keyword
            OR color LIKE :keyword
        )
        ORDER BY bike_id DESC
    """)

    with engine.connect() as conn:
        bikes = conn.execute(
            query,
            {
                "keyword": f"%{keyword}%"
            }
        ).mappings().all()

    return bikes
# =========================
# Update Bike
# =========================
@router.put("/{bike_id}")
def update_bike(
    bike_id: int,
    bike: BikeUpdate
):

    query = text("""
        UPDATE bikes
        SET
            brand = :brand,
            model = :model,
            variant = :variant,
            color = :color,
            engine_no = :engine_no,
            chassis_no = :chassis_no,
            ex_showroom_price = :ex_showroom_price,
            stock_quantity = :stock_quantity
        WHERE bike_id = :bike_id
        AND is_active = 1
    """)

    data = bike.model_dump()
    data["bike_id"] = bike_id

    with engine.begin() as conn:

        result = conn.execute(query, data)

        if result.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail="Bike Not Found"
            )

    return {
        "message": "Bike Updated Successfully"
    }
# =========================
# Soft Delete Bike
# =========================
@router.delete("/{bike_id}")
def delete_bike(bike_id: int):

    query = text("""
        UPDATE bikes
        SET is_active = 0
        WHERE bike_id = :bike_id
        AND is_active = 1
    """)

    with engine.begin() as conn:

        result = conn.execute(
            query,
            {"bike_id": bike_id}
        )

        if result.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail="Bike Not Found"
            )

    return {
        "message": "Bike Deleted Successfully"
    }