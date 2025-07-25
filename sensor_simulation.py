import asyncio
import random
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from database import engine
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import sqlalchemy.exc

class DeviceSensorData:
    def __init__(self, ship_id, device_id, sensor_values, corroction_status):
        self.ship_id = ship_id
        self.device_id = device_id
        self.sensor_values = sensor_values  # dict with keys sensor1-4
        self.corroction_status = corroction_status
        self.timestamp = datetime.now(ZoneInfo("Asia/Jakarta"))

device_count = 4

async def register_devices_for_active_ships():
    async with AsyncSession(engine) as session:
        result = await session.execute(
            text("SELECT \"IMO_NUMBER\" FROM ships WHERE status = 'Active'")
        )
        active_ships = [row[0] for row in result.fetchall()]
        for ship_id in active_ships:
            for i in range(1, device_count+1):
                device_id = f"{ship_id}_device_{i}"
                await session.execute(
                    text("""
                        INSERT INTO ship_device (device_id, id_ship)
                        VALUES (:device_id, :id_ship)
                        ON CONFLICT (device_id) DO NOTHING
                    """),
                    {'device_id': device_id, 'id_ship': ship_id}
                )
        await session.commit()
    return active_ships

async def device_sensor_simulator(ship_id: str, device_num: int, queue: asyncio.Queue):
    while True:
        sensor_values = {
            'sensor1': str(round(random.uniform(10, 25), 2)),
            'sensor2': str(round(random.uniform(10, 25), 2)),
            'sensor3': str(round(random.uniform(10, 25), 2)),
            'sensor4': str(round(random.uniform(10, 25), 2)),
        }
        corroction_status = random.choice(["Low", "Medium", "High"])
        device_id = f"{ship_id}_device_{device_num}"
        data = DeviceSensorData(ship_id, device_id, sensor_values, corroction_status)
        await queue.put(data)
        await asyncio.sleep(1)

async def collector(ship_id: str, queue: asyncio.Queue, collector_semaphore):
    async with collector_semaphore:
        while True:
            data: DeviceSensorData = await queue.get()
            for attempt in range(3):  # Try up to 3 times
                try:
                    async with AsyncSession(engine) as session:
                        await session.execute(
                            text("""
                                INSERT INTO monitor_ship_log (device_id, sensor1, sensor2, sensor3, sensor4, corroction_status, timestamp)
                                VALUES (:device_id, :sensor1, :sensor2, :sensor3, :sensor4, :corroction_status, :timestamp)
                            """),
                            {
                                'device_id': data.device_id,
                                'sensor1': data.sensor_values['sensor1'],
                                'sensor2': data.sensor_values['sensor2'],
                                'sensor3': data.sensor_values['sensor3'],
                                'sensor4': data.sensor_values['sensor4'],
                                'corroction_status': data.corroction_status,
                                'timestamp': data.timestamp.replace(tzinfo=None)
                            }
                        )
                        device_num = int(data.device_id.split('_')[-1])
                        device_col = f"device{device_num}"
                        await session.execute(
                            text(f"""
                                INSERT INTO ship_monitor (id_ship, device1, device2, device3, device4)
                                VALUES (:id_ship, NULL, NULL, NULL, NULL)
                                ON CONFLICT (id_ship) DO NOTHING
                            """),
                            {'id_ship': data.ship_id}
                        )
                        await session.execute(
                            text(f"""
                                UPDATE ship_monitor SET {device_col} = :corroction_status WHERE id_ship = :id_ship
                            """),
                            {'id_ship': data.ship_id, 'corroction_status': data.corroction_status}
                        )
                        await session.commit()
                    break  # Success, exit retry loop
                except (sqlalchemy.exc.DBAPIError, sqlalchemy.exc.OperationalError) as e:
                    print(f"DB error: {e}, retrying...")
                    await asyncio.sleep(1)
                except Exception as e:
                    print(f"Unexpected error: {e}")
                    break
            print(f"Updated {data.device_id}: {data.sensor_values}, corroction_status={data.corroction_status}")
            await asyncio.sleep(60)

async def simulate_and_write(ship_id: str, collector_semaphore):
    # Check if ship is still active before starting simulation
    async with AsyncSession(engine) as session:
        result = await session.execute(
            text('SELECT status FROM ships WHERE "IMO_NUMBER" = :ship_id'),
            {"ship_id": ship_id}
        )
        row = result.fetchone()
        if not row or row[0] != 'Active':
            print(f"Ship {ship_id} is not active. Skipping simulation.")
            return
    queue = asyncio.Queue()
    device_tasks = [asyncio.create_task(device_sensor_simulator(ship_id, i, queue)) for i in range(1, device_count+1)]
    collector_task = asyncio.create_task(collector(ship_id, queue, collector_semaphore))
    await asyncio.gather(*device_tasks, collector_task) 