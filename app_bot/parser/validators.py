import pytz
from pydantic import BaseModel, field_validator
from datetime import datetime


class StationData(BaseModel):
    id: int
    name: str | None
    number: str | None
    region_name: str | None
    federal_district: str | None
    address: str | None
    status: str | None
    longitude: str | None
    latitude: str | None
    updated_at: datetime | None

    @field_validator('updated_at')
    @classmethod
    def set_moscow_timezone(cls, v):
        if v is None:
            return v

        moscow_tz = pytz.timezone('Europe/Moscow')
        return v.astimezone(moscow_tz)


class ProductData(BaseModel):
    station_id: int
    product_code: str | None
    product_name: str | None
    price: float | None
    date: datetime | None

    @field_validator('date')
    @classmethod
    def set_moscow_timezone(cls, v):
        if v is None:
            return v

        moscow_tz = pytz.timezone('Europe/Moscow')
        return v.astimezone(moscow_tz)

    @field_validator('price')
    @classmethod
    def convert_price_to_float(cls, v):
        if v is None:
            return v

        return float(v)
