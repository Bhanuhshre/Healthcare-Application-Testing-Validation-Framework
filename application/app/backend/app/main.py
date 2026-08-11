"""
Application entrypoint.

Run locally with:
    uvicorn app.main:app --reload --app-dir application/backend

The interactive API docs are then available at /docs.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.db import Base, engine
from app.api import patients, doctors, appointments, auth

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Clinic Scheduling API",
    description="Backend for patient records, doctor rosters and appointment scheduling.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(patients.router)
app.include_router(doctors.router)
app.include_router(appointments.router)


@app.get("/health")
def health_check():
    """Used by the CI pipeline and uptime checks to confirm the service is up."""
    return {"status": "ok"}
