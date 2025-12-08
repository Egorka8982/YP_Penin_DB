
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from .db import SessionLocal, engine, Base
from . import crud, schemas

# Создание таблиц, если не применяли init.sql
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Hospital MIS API")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/patients", response_model=list[schemas.PatientOut])
def patients(db: Session = Depends(get_db)):
    return crud.list_patients(db)


@app.post("/patients", response_model=schemas.PatientOut, status_code=201)
def add_patient(payload: schemas.PatientCreate, db: Session = Depends(get_db)):
    return crud.create_patient(db, payload)


@app.get("/doctors", response_model=list[schemas.DoctorOut])
def doctors(db: Session = Depends(get_db)):
    return crud.list_doctors(db)


@app.post("/doctors", response_model=schemas.DoctorOut, status_code=201)
def add_doctor(payload: schemas.DoctorCreate, db: Session = Depends(get_db)):
    return crud.create_doctor(db, payload)


@app.get("/services", response_model=list[schemas.ServiceOut])
def services(db: Session = Depends(get_db)):
    return crud.list_services(db)


@app.post("/services", response_model=schemas.ServiceOut, status_code=201)
def add_service(payload: schemas.ServiceCreate, db: Session = Depends(get_db)):
    return crud.create_service(db, payload)


@app.get("/appointments", response_model=list[schemas.AppointmentOut])
def appointments(
    doctor_id: int | None = None, patient_id: int | None = None, db: Session = Depends(get_db)
):
    return crud.list_appointments(db, doctor_id, patient_id)


@app.post("/appointments", response_model=schemas.AppointmentOut, status_code=201)
def add_appointment(payload: schemas.AppointmentCreate, db: Session = Depends(get_db)):
    return crud.create_appointment(db, payload)

