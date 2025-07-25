from fastapi import FastAPI
from database import engine
from api.monitor_ship import router as monitor_ship_router
from api.ship import router as ship_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Or ["*"] for all origins (not recommended for production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(monitor_ship_router)
app.include_router(ship_router)

@app.get("/")
async def root():
    return {"message": "Sensor generator running!"} 