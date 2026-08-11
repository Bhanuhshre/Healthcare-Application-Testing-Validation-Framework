from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.database.models import Appointment, Patient, Doctor
from app.schemas import AppointmentCreate, AppointmentOut, AppointmentStatusUpdate
from app.core.deps import require_role
from app.core.scheduling import has_conflict, is_in_the_past

router = APIRouter(prefix="/api/appointments", tags=["appointments"])


@router.post("", response_model=AppointmentOut, status_code=status.HTTP_201_CREATED)
def create_appointment(
    payload: AppointmentCreate,
    db: Session = Depends(get_db),
    _user=Depends(require_role("admin", "staff")),
):
    patient = db.query(Patient).filter(Patient.id == payload.patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    doctor = db.query(Doctor).filter(Doctor.id == payload.doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    if is_in_the_past(payload.scheduled_at):
        raise HTTPException(status_code=400, detail="Cannot schedule an appointment in the past")

    existing_times = [
        appt.scheduled_at
        for appt in db.query(Appointment)
        .filter(
            Appointment.doctor_id == payload.doctor_id,
            Appointment.status == "scheduled",
        )
        .all()
    ]
    if has_conflict(payload.scheduled_at, existing_times):
        raise HTTPException(
            status_code=409,
            detail="This doctor already has an appointment too close to the requested time",
        )

    appointment = Appointment(**payload.model_dump())
    db.add(appointment)
    db.commit()
    db.refresh(appointment)
    return appointment


@router.get("", response_model=List[AppointmentOut])
def list_appointments(
    patient_id: int = None,
    doctor_id: int = None,
    db: Session = Depends(get_db),
    _user=Depends(require_role("admin", "staff", "doctor")),
):
    query = db.query(Appointment)
    if patient_id is not None:
        query = query.filter(Appointment.patient_id == patient_id)
    if doctor_id is not None:
        query = query.filter(Appointment.doctor_id == doctor_id)
    return query.order_by(Appointment.scheduled_at).all()


@router.patch("/{appointment_id}/status", response_model=AppointmentOut)
def update_status(
    appointment_id: int,
    payload: AppointmentStatusUpdate,
    db: Session = Depends(get_db),
    _user=Depends(require_role("admin", "staff", "doctor")),
):
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    appointment.status = payload.status
    db.commit()
    db.refresh(appointment)
    return appointment
