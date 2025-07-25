from pydantic import BaseModel
from typing import Optional

class MonitorShip(BaseModel):
    device_id: str
    sensor_value: str
    corroction_status: str
    timestamp: Optional[str] = None

class ShipMonitor(BaseModel):
    id_ship: str
    device_1: str
    device_2: str
    device_3: str
    device_4: str

class Ship(BaseModel):
    shipName: str
    IMO_NUMBER: str
    Year_built: int
    owner: str
    location_from: str
    location_to: str
    Coordinate_x: float
    Coordinate_y: float
    owner_contact: str
    status: str
    user_id: Optional[int] = None 