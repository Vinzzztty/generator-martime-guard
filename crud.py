from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from database import engine
from typing import Optional

async def get_monitor_ships():
    async with AsyncSession(engine) as session:
        result = await session.execute(text("SELECT * FROM ship_monitor"))
        rows = result.fetchall()
        return [dict(row._mapping) for row in rows]

async def add_monitor_ship(ship):
    # This function is ambiguous with new schema; skipping or refactoring may be needed based on new requirements.
    pass

async def add_or_update_ship(ship):
    async with AsyncSession(engine) as session:
        await session.execute(
            text("""
                INSERT INTO ships (shipName, "IMO_NUMBER", Year_built, owner, location_from, location_to, Coordinate_x, Coordinate_y, owner_contact, status)
                VALUES (:shipName, :IMO_NUMBER, :Year_built, :owner, :location_from, :location_to, :Coordinate_x, :Coordinate_y, :owner_contact, :status)
                ON CONFLICT ("IMO_NUMBER") DO UPDATE SET
                    shipName = EXCLUDED.shipName,
                    Year_built = EXCLUDED.Year_built,
                    owner = EXCLUDED.owner,
                    location_from = EXCLUDED.location_from,
                    location_to = EXCLUDED.location_to,
                    Coordinate_x = EXCLUDED.Coordinate_x,
                    Coordinate_y = EXCLUDED.Coordinate_y,
                    owner_contact = EXCLUDED.owner_contact,
                    status = EXCLUDED.status
            """),
            ship.dict()
        )
        await session.commit()

async def get_ships_with_all_devices():
    async with AsyncSession(engine) as session:
        result = await session.execute(text("""
            SELECT s.*, sm.device1, sm.device2, sm.device3, sm.device4
            FROM ships s
            LEFT JOIN ship_monitor sm ON s."IMO_NUMBER" = sm.id_ship
        """))
        rows = result.fetchall()
        ships = []
        for row in rows:
            ship = dict(row._mapping)
            ship["is_active"] = (ship.get("status") == "Active")
            ships.append(ship)
        return ships
    
async def get_ships_with_devices_active():
    async with AsyncSession(engine) as session:
        result = await session.execute(text("""
            SELECT s.*, sm.device1, sm.device2, sm.device3, sm.device4
            FROM ships s
            LEFT JOIN ship_monitor sm ON s."IMO_NUMBER" = sm.id_ship
            WHERE status = 'Active'
        """))
        rows = result.fetchall()
        ships = []
        for row in rows:
            ship = dict(row._mapping)
            ship["is_active"] = (ship.get("status") == "Active")
            ships.append(ship)
        return ships

async def get_active_ships():
    async with AsyncSession(engine) as session:
        result = await session.execute(
            text('SELECT "IMO_NUMBER", user_id FROM ships WHERE status = :status'),
            {"status": "Active"}
        )
        rows = result.fetchall()
        return [{"IMO_NUMBER": row[0], "user_id": row[1]} for row in rows]

async def get_ships():
    async with AsyncSession(engine) as session:
        result = await session.execute(text('SELECT * FROM ships'))
        rows = result.fetchall()
        return [dict(row._mapping) for row in rows]

async def get_monitor_devices_sensor(limit=50):
    async with AsyncSession(engine) as session:
        result = await session.execute(
            text('''
                SELECT l.id, l.device_id, d.id_ship, l.timestamp, l.corroction_status, l.sensor1, l.sensor2, l.sensor3, l.sensor4
                FROM monitor_ship_log l
                JOIN ship_device d ON l.device_id = d.device_id
                ORDER BY l.timestamp DESC
                LIMIT :limit
            '''),
            {"limit": limit}
        )
        rows = result.fetchall()
        return [dict(row._mapping) for row in rows]

async def get_simple_log(limit=50):
    async with AsyncSession(engine) as session:
        result = await session.execute(
            text('SELECT id_ship, device1, device2, device3, device4, timestamp FROM monitor_ship_log ORDER BY timestamp DESC LIMIT :limit'),
            {"limit": limit}
        )
        rows = result.fetchall()
        log_lines = [
            f"{row.id_ship} | {row.device1}, {row.device2}, {row.device3}, {row.device4} | {row.timestamp}"
            for row in rows
        ]
        return {"log": log_lines}

async def get_monitor_ship_by_id(id_ship):
    async with AsyncSession(engine) as session:
        result = await session.execute(
            text("SELECT * FROM ship_monitor WHERE id_ship = :id_ship"),
            {"id_ship": id_ship}
        )
        row = result.fetchone()
        return dict(row._mapping) if row else None

async def get_monitor_ship_log_by_id(id_ship, limit=50, device_id: Optional[str] = None):
    async with AsyncSession(engine) as session:
        if device_id:
            result = await session.execute(
                text("""
                    SELECT l.*
                    FROM monitor_ship_log l
                    JOIN ship_device d ON l.device_id = d.device_id
                    WHERE d.id_ship = :id_ship AND l.device_id = :device_id
                    ORDER BY l.timestamp DESC
                    LIMIT :limit
                """),
                {"id_ship": id_ship, "device_id": device_id, "limit": limit}
            )
        else:
            result = await session.execute(
                text("""
                    SELECT l.*
                    FROM monitor_ship_log l
                    JOIN ship_device d ON l.device_id = d.device_id
                    WHERE d.id_ship = :id_ship
                    ORDER BY l.timestamp DESC
                    LIMIT :limit
                """),
                {"id_ship": id_ship, "limit": limit}
            )
        rows = result.fetchall()
        return [dict(row._mapping) for row in rows]

async def get_monitor_ship_log_by_device_id(device_id, limit=50):
    async with AsyncSession(engine) as session:
        result = await session.execute(
            text("SELECT * FROM monitor_ship_log WHERE device_id = :device_id ORDER BY timestamp DESC LIMIT :limit"),
            {"device_id": device_id, "limit": limit}
        )
        rows = result.fetchall()
        return [dict(row._mapping) for row in rows] 

async def get_monitor_devices_sensor_by_ship_id(id_ship, limit=50):
    async with AsyncSession(engine) as session:
        result = await session.execute(
            text('''
                SELECT l.id, l.device_id, d.id_ship, l.timestamp, l.corroction_status, l.sensor1, l.sensor2, l.sensor3, l.sensor4
                FROM monitor_ship_log l
                JOIN ship_device d ON l.device_id = d.device_id
                WHERE d.id_ship = :id_ship
                ORDER BY l.timestamp DESC
                LIMIT :limit
            '''),
            {"id_ship": id_ship, "limit": limit}
        )
        rows = result.fetchall()
        return [dict(row._mapping) for row in rows] 