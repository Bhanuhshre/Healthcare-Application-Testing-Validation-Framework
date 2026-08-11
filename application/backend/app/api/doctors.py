from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.database.models import Doctor
from app.schemas import DoctorCreate, DoctorOut
from app.core.deps import require_role

router = APIRouter(prefix="/api/doctors", tags=["doctors"])


@router.post("", response_model=DoctorOut, status_code=status.HTTP_201_CREATED)
def create_doctor(
    payload: DoctorCreate,
    db: Session = Depends(get_db),
    _user=Depends(require_role("admin")),
):
    existing = db.query(Doctor).filter(Doctor.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="A doctor with this email already exists")

    doctor = Doctor(**payload.model_dump())
    db.add(doctor)
    db.commit()
    db.refresh(doctor)
    return doctor


@router.get("", response_model=List[DoctorOut])
def list_doctors(
    db: Session = Depends(get_db),
    _user=Depends(require_role("admin", "staff", "doctor")),
):
    return db.query(Doctor).filter(Doctor.is_active.is_(True)).all()
