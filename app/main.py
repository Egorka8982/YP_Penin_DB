"""
FastAPI приложение для системы медицинского учёта.

БЕЗОПАСНОСТЬ ОТ SQL-ИНЪЕКЦИЙ:
- Все CRUD операции используют ORM SQLAlchemy (см. app/crud.py)
- Входные данные валидируются через Pydantic-схемы перед обработкой
- Параметры запросов (doctor_id, patient_id) автоматически параметризуются ORM
- Нет прямого выполнения сырых SQL-запросов
"""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from .db import SessionLocal, engine, Base
from . import crud, schemas

# Создание таблиц, если не применяли init.sql
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Hospital MIS API")
security = HTTPBasic()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def require_role(allowed_roles: list[str]):

    def dep(creds: HTTPBasicCredentials = Depends(security)):
        users = {
            "admin": ("admin_pass", "admin"),
            "manager": ("manager_pass", "manager"),
            "staff": ("staff_pass", "staff"),
            "readonly": ("readonly_pass", "readonly"),
        }
        if creds.username not in users or users[creds.username][0] != creds.password:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
                headers={"WWW-Authenticate": "Basic"},
            )
        role = users[creds.username][1]
        if role not in allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
        return role

    return dep


@app.get("/patients", response_model=list[schemas.PatientOut])
def patients(
    db: Session = Depends(get_db),
    _: str = Depends(require_role(["admin", "manager", "staff", "readonly"])),
):
    return crud.list_patients(db)


@app.post("/patients", response_model=schemas.PatientOut, status_code=201)
def add_patient(
    payload: schemas.PatientCreate,
    db: Session = Depends(get_db),
    _: str = Depends(require_role(["admin", "manager"])),
):
    return crud.create_patient(db, payload)


@app.get("/doctors", response_model=list[schemas.DoctorOut])
def doctors(
    db: Session = Depends(get_db),
    _: str = Depends(require_role(["admin", "manager", "staff", "readonly"])),
):
    return crud.list_doctors(db)


@app.post("/doctors", response_model=schemas.DoctorOut, status_code=201)
def add_doctor(
    payload: schemas.DoctorCreate,
    db: Session = Depends(get_db),
    _: str = Depends(require_role(["admin", "manager"])),
):
    return crud.create_doctor(db, payload)


@app.get("/services", response_model=list[schemas.ServiceOut])
def services(
    db: Session = Depends(get_db),
    _: str = Depends(require_role(["admin", "manager", "staff", "readonly"])),
):
    return crud.list_services(db)


@app.post("/services", response_model=schemas.ServiceOut, status_code=201)
def add_service(
    payload: schemas.ServiceCreate,
    db: Session = Depends(get_db),
    _: str = Depends(require_role(["admin", "manager"])),
):
    return crud.create_service(db, payload)


@app.get("/appointments", response_model=list[schemas.AppointmentOut])
def appointments(
    doctor_id: int | None = None,
    patient_id: int | None = None,
    db: Session = Depends(get_db),
    _: str = Depends(require_role(["admin", "manager", "staff", "readonly"])),
):
    """
    Получить список приёмов с фильтрацией.
    Безопасно: параметры doctor_id и patient_id автоматически валидируются FastAPI как int,
    затем передаются в ORM filter(), который параметризует запрос.
    """
    return crud.list_appointments(db, doctor_id, patient_id)


@app.post("/appointments", response_model=schemas.AppointmentOut, status_code=201)
def add_appointment(
    payload: schemas.AppointmentCreate,
    db: Session = Depends(get_db),
    _: str = Depends(require_role(["admin", "manager"])),
):
    return crud.create_appointment(db, payload)



@app.exception_handler(IntegrityError)
async def integrity_error_handler(request, exc: IntegrityError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": "Integrity error"},
    )


@app.exception_handler(Exception)
async def unhandled_error_handler(request, exc: Exception):

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )

