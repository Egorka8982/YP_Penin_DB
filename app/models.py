from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    Text,
    ForeignKey,
    DECIMAL,
    CheckConstraint,
    TIMESTAMP,
)
from sqlalchemy.orm import relationship
from .db import Base


class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True)
    full_name = Column(String(200), nullable=False)
    birth_date = Column(Date, nullable=False)
    phone = Column(String(20), nullable=False, unique=True)
    email = Column(String(120), unique=True)
    created_at = Column(TIMESTAMP)

    appointments = relationship("Appointment", back_populates="patient", cascade="all, delete")


class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True)
    full_name = Column(String(200), nullable=False)
    specialty = Column(String(120), nullable=False)
    room = Column(String(20))
    phone = Column(String(20))
    created_at = Column(TIMESTAMP)

    appointments = relationship("Appointment", back_populates="doctor")


class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False, unique=True)
    price = Column(DECIMAL(10, 2), nullable=False)
    duration_minutes = Column(Integer, nullable=False)

    __table_args__ = (
        CheckConstraint("price >= 0"),
        CheckConstraint("duration_minutes > 0"),
    )


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("doctors.id", ondelete="RESTRICT"), nullable=False)
    scheduled_at = Column(TIMESTAMP, nullable=False)
    status = Column(String(30), nullable=False)
    notes = Column(Text)
    created_at = Column(TIMESTAMP)

    patient = relationship("Patient", back_populates="appointments")
    doctor = relationship("Doctor", back_populates="appointments")
    services = relationship(
        "AppointmentService",
        back_populates="appointment",
        cascade="all, delete",
    )


class AppointmentService(Base):
    __tablename__ = "appointment_services"

    appointment_id = Column(
        Integer, ForeignKey("appointments.id", ondelete="CASCADE"), primary_key=True
    )
    service_id = Column(Integer, ForeignKey("services.id", ondelete="RESTRICT"), primary_key=True)
    quantity = Column(Integer, nullable=False, default=1)

    appointment = relationship("Appointment", back_populates="services")
    service = relationship("Service")

