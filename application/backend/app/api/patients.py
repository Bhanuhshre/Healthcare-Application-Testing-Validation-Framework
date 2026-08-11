from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.database.models import Patient
from app.schemas import PatientCreate, PatientOut, PatientUpdate
from app.core.mrn import generate_mrn
from app.core.deps import require_role

router = APIRouter(prefix="/api/patients", tags=["patients"])


@router.post("", response_model=PatientOut, status_code=status.HTTP_201_CREATED)
def create_patient(
    payload: PatientCreate,
    db: Session = Depends(get_db),
    _user=Depends(require_role("admin", "staff")),
):
    if payload.email:
        existing = db.query(Patient).filter(Patient.email == payload.email).first()
        if existing:
            raise HTTPException(status_code=400, detail="A patient with this email already exists")

    count = db.query(Patient).count()
    mrn = generate_mrn(sequence=count + 1)

    patient = Patient(
        full_name=payload.full_name,
        date_of_birth=payload.date_of_birth,
        contact_number=payload.contact_number,
        email=payload.email,
        medical_record_number=mrn,
    )
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient


@router.get("", response_model=List[PatientOut])
def list_patients(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    _user=Depends(require_role("admin", "staff", "doctor")),
):
    return db.query(Patient).offset(skip).limit(limit).all()


@router.get("/{patient_id}", response_model=PatientOut)
def get_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    _user=Depends(require_role("admin", "staff", "doctor")),
):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient


@router.patch("/{patient_id}", response_model=PatientOut)
def update_patient(
    patient_id: int,
    payload: PatientUpdate,
    db: Session = Depends(get_db),
    _user=Depends(require_role("admin", "staff")),
):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(patient, field, value)

    db.commit()
    db.refresh(patient)
    return patient


@router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    _user=Depends(require_role("admin")),
):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    db.delete(patient)
    db.commit()
    return None
