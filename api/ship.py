from fastapi import APIRouter
from models import Ship
import crud

router = APIRouter()

@router.post("/ships")
async def add_or_update_ship(ship: Ship):
    await crud.add_or_update_ship(ship)
    return {"message": "Ship added/updated"}

@router.get("/ships_with_all_devices")
async def get_ships_with_all_devices():
    return await crud.get_ships_with_all_devices()

@router.get("/ships_with_devices_active")
async def get_ships_with_devices_active():
    return await crud.get_ships_with_devices_active()

@router.get("/active_ships")
async def get_active_ships():
    return await crud.get_active_ships()

@router.get("/ships")
async def get_ships():
    return await crud.get_ships() 