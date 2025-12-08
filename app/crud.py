from sqlalchemy.orm import Session
from . import models, schemas


def list_patients(db: Session):
    return db.query(models.Patient).all()


def create_patient(db: Session, data: schemas.PatientCreate):
    obj = models.Patient(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def list_doctors(db: Session):
    return db.query(models.Doctor).all()


def create_doctor(db: Session, data: schemas.DoctorCreate):
    obj = models.Doctor(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def list_services(db: Session):
    return db.query(models.Service).all()


def create_service(db: Session, data: schemas.ServiceCreate):
    obj = models.Service(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def create_appointment(db: Session, data: schemas.AppointmentCreate):
    appt = models.Appointment(
        patient_id=data.patient_id,
        doctor_id=data.doctor_id,
        scheduled_at=data.scheduled_at,
        status=data.status,
        notes=data.notes,
    )
    db.add(appt)
    for item in data.services:
        db.add(
            models.AppointmentService(
                appointment=appt,
                service_id=item.service_id,
                quantity=item.quantity,
            )
        )
    db.commit()
    db.refresh(appt)
    return appt


def list_appointments(db: Session, doctor_id=None, patient_id=None):
    q = db.query(models.Appointment)
    if doctor_id:
        q = q.filter(models.Appointment.doctor_id == doctor_id)
    if patient_id:
        q = q.filter(models.Appointment.patient_id == patient_id)
    return q.all()

