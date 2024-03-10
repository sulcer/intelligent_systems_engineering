from pydantic import BaseModel


class Station(BaseModel):
    number: int
    contract_name: str
    name: str
    address: str
    position: dict
    banking: bool
    bonus: bool
    bike_stands: int
    available_bike_stands: int
    available_bikes: int
    status: str
    last_update: int
