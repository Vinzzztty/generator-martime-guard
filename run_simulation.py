import asyncio
from sensor_simulation import simulate_and_write, register_devices_for_active_ships
import crud

async def main():
    active_ships = await register_devices_for_active_ships()
    print("Active ships for simulation:", active_ships)
    collector_semaphore = asyncio.Semaphore(2)  # Create inside the event loop
    tasks = [asyncio.create_task(simulate_and_write(ship_id, collector_semaphore)) for ship_id in active_ships]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main()) 