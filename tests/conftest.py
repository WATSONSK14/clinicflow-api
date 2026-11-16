# tests/conftest.py
import os
os.environ["TESTING"] = "1"

import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from app.database import Base, get_db
from app.models.enums import UserRole
from app.models.user import User
from app.models.doctor import Doctor
from app.models.time_slot import TimeSlot
from app.core.security import hash_password, create_access_token


SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()

    # Slotları otomatik tohumla (08:00 - 18:00 arası 20 slot)
    start_dt = datetime.strptime("08:00", "%H:%M")
    end_boundary = datetime.strptime("18:00", "%H:%M")
    while start_dt < end_boundary:
        slot_end = start_dt + timedelta(minutes=30)
        session.add(TimeSlot(
            start_time=start_dt.strftime("%H:%M"),
            end_time=slot_end.strftime("%H:%M")
        ))
        start_dt = slot_end
    session.commit()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()



@pytest.fixture
def test_patient(db):
    def _create_patient(**kwargs):
        user = User(
            email=kwargs.get("email","patient@test.com"),
            full_name="Test Hasta",
            phone_number="05550001122",
            hashed_password=hash_password("Pass123!"),
            role=UserRole.PATIENT,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    return _create_patient



@pytest.fixture
def patient_token():
    def _create_token(patient):
        return create_access_token(
            data={"sub": str(patient.id), "role": patient.role.value}
        )
    return _create_token


@pytest.fixture
def test_doctor(db):
    def _create_doctor(**kwargs):
        user = User(
            email=kwargs.get("email", "doctor@test.com"),
            full_name="Dr. Test Hekim",
            phone_number="05550003344",
            hashed_password=hash_password(
                "DocPass123!"),
            role=UserRole.DOCTOR,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        doctor = Doctor(
            user_id=user.id,
            specialty=kwargs.get("specialty", "Kardiyoloji"),
            room_number=kwargs.get("room_number", "K-101"),
            working_start=kwargs.get("working_start", "09:00"),
            working_end=kwargs.get("working_end", "17:00"),
        )
        db.add(doctor)
        db.commit()
        db.refresh(doctor)

        return doctor
    return _create_doctor