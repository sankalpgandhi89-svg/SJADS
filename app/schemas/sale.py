from pydantic import BaseModel
from datetime import date
from typing import Literal


class SaleCreate(BaseModel):
    customer_id: int
    bike_id: int
    quantity: int
    selling_price: float
    payment_mode: Literal["Cash", "Finance"]
    sale_date: date


class SaleUpdate(BaseModel):
    customer_id: int
    bike_id: int
    quantity: int
    selling_price: float
    payment_mode: Literal["Cash", "Finance"]
    sale_date: date