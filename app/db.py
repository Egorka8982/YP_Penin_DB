from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Используем роль manager по умолчанию (ограниченные права для приложения)
DATABASE_URL = "postgresql+psycopg2://manager:manager_pass@localhost:5432/hospital_mis"

engine = create_engine(DATABASE_URL, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)
Base = declarative_base()

