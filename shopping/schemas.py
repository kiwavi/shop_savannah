from pydantic import BaseModel, Field, validator
from typing import Optional
import re

class OrderDetails(BaseModel):
    phone_number: str = Field(...,description="Should a Kenyan phone number format (+254..., 0(1/7)..)")
    address: str = Field(...,description="Your delivery address")
    other_details: Optional[str] = Field(None, description="Other details pertaining to your specific order")

    @validator("phone_number")
    def phone_number_validator(cls,v):
        pattern = r"^(?:\+254|0)(?:1|7)[0-9]{8}$"
        if not re.match(pattern, v):
            raise ValueError("Invalid Kenyan phone number format")
        return v
