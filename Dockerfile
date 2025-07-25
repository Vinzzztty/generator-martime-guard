FROM python:3.9-slim

WORKDIR /app

COPY . .

RUN pip install --upgrade pip \
    && pip install fastapi uvicorn sqlalchemy asyncpg pydantic python-dotenv

# Default: run API service. Override CMD in docker-compose for simulation.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8005"] 