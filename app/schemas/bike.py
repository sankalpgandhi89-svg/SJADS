from pydantic import BaseModel
from typing import Optional


class BikeCreate(BaseModel):
    brand: str
    model: str
    variant: Optional[str] = None
    color: Optional[str] = None
    engine_no: Optional[str] = None
    chassis_no: Optional[str] = None
    ex_showroom_price: float
    stock_quantity: int = 0


class BikeUpdate(BaseModel):
    brand: str
    model: str
    variant: Optional[str] = None
    color: Optional[str] = None
    engine_no: Optional[str] = None
    chassis_no: Optional[str] = None
    ex_showroom_price: float
    stock_quantity: int