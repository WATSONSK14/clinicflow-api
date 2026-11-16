# main.py
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

import app.models  # noqa: F401  (tum modelleri metadata'ya kaydeder)
from app.database import engine, Base
from app.routers import auth, doctor, appointments
from seed import seed


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Testler kendi in-memory DB'sini kullanir; gercek DB'ye dokunma
    if os.getenv("TESTING") != "1":
        Base.metadata.create_all(bind=engine)
        seed()
    yield


app = FastAPI(
    title="ClinicFlow API",
    description="Healthcare & Appointment Scheduling API",
    version="1.0.0",
    lifespan=lifespan,
)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(auth.router)
app.include_router(doctor.router)
app.include_router(appointments.router)


@app.get("/", include_in_schema=False)
def root():
    return FileResponse("static/index.html")


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}