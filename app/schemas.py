from datetime import datetime, date
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class PatientCreate(BaseModel):
    full_name: str
    birth_date: date
    phone: str
    email: Optional[str] = None


class PatientOut(PatientCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)


class DoctorCreate(BaseModel):
    full_name: str
    specialty: str
    room: Optional[str] = None
    phone: Optional[str] = None


class DoctorOut(DoctorCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)


class ServiceCreate(BaseModel):
    name: str
    price: float = Field(..., ge=0)
    duration_minutes: int = Field(..., gt=0)


class ServiceOut(ServiceCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)


class AppointmentServiceItem(BaseModel):
    service_id: int
    quantity: int = Field(..., gt=0)


class AppointmentCreate(BaseModel):
    patient_id: int
    doctor_id: int
    scheduled_at: datetime
    status: str
    notes: Optional[str] = None
    services: List[AppointmentServiceItem] = []


class AppointmentOut(BaseModel):
    id: int
    patient_id: int
    doctor_id: int
    scheduled_at: datetime
    status: str
    notes: Optional[str]
    services: List[AppointmentServiceItem]
    model_config = ConfigDict(from_attributes=True)

