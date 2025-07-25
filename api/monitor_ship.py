from fastapi import APIRouter, HTTPException, status
from typing import List
import crud

router = APIRouter()

@router.get("/ship_monitors_active_device", response_model=List[dict])
async def get_ship_monitors():
    try:
        return await crud.get_monitor_ships()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ship_monitors_active_device/{id_ship}")
async def get_ship_monitor_by_id(id_ship: str):
    try:
        result = await crud.get_monitor_ship_by_id(id_ship)
        if result:
            return result
        raise HTTPException(status_code=404, detail="id_ship not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/monitor_ship_log/{id_ship}", response_model=List[dict])
async def get_monitor_ship_log_by_id(id_ship: str, limit: int = 50, device_id: str = None):
    """
    Get logs for a ship (all devices) or a specific device of a ship if device_id is provided.
    """
    try:
        return await crud.get_monitor_ship_log_by_id(id_ship, limit, device_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/monitor_ship_log/device/{device_id}", response_model=List[dict])
async def get_monitor_ship_log_by_device_id(device_id: str, limit: int = 50):
    try:
        return await crud.get_monitor_ship_log_by_device_id(device_id, limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/monitor-devices-sensor/", response_model=List[dict])
async def get_monitor_devices_sensor_endpoint(limit: int = 50):
    """
    Get the latest monitor devices sensor logs, limited by the 'limit' parameter.
    """
    try:
        return await crud.get_monitor_devices_sensor(limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/monitor-devices-sensor/{id_ship}", response_model=List[dict])
async def get_monitor_devices_sensor_by_ship_id_endpoint(id_ship: str, limit: int = 50):
    """
    Get the latest monitor devices sensor logs for a specific ship, limited by the 'limit' parameter.
    """
    try:
        return await crud.get_monitor_devices_sensor_by_ship_id(id_ship, limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 