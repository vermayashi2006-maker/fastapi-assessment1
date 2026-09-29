from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database import create_db_and_tables
from app.routers import items, events

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(
    title="Campus Management APIs (FastAPI Assessment)",
    version="1.0.0",
    lifespan=lifespan
)

#this is very important to connect these router
app.include_router(items.router)
app.include_router(events.router)

@app.get("/")
def root():
    return {"message": "Campus API is running. Go to /docs for Swagger UI."}