from pydantic import BaseModel
from typing import Optional
from datetime import date


class CustomerCreate(BaseModel):
    full_name: str
    mobile: str
    email: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    aadhaar: Optional[str] = None
    pan: Optional[str] = None
    date_of_birth: Optional[date] = None