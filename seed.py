from datetime import datetime, timedelta
from sqlalchemy import select
from app.database import SessionLocal
from app.models.enums import UserRole
from app.models.user import User
from app.models.doctor import Doctor
from app.models.time_slot import TimeSlot
from app.core.security import hash_password


def seed():
    db = SessionLocal()
    try:
        existing_slots = db.execute(select(TimeSlot)).scalars().all()
        if not existing_slots:
            print("TimeSlot'lar olusturuluyor...")
            start_dt = datetime.strptime("08:00", "%H:%M")
            end_boundary = datetime.strptime("18:00", "%H:%M")

            while start_dt < end_boundary:
                slot_end = start_dt + timedelta(minutes=30)
                start_str = start_dt.strftime("%H:%M")
                end_str = slot_end.strftime("%H:%M")

                slot = TimeSlot(start_time=start_str, end_time=end_str)
                db.add(slot)
                start_dt = slot_end

            db.commit()
            print("20 adet TimeSlot basariyla eklendi!")


        admin = db.execute(select(User).filter_by(email="admin@clinicflow.com")).scalar_one_or_none()
        if not admin:
            admin = User(
                email="admin@clinicflow.com",
                full_name="Bashekim Watson",
                phone_number="05551112233",
                hashed_password=hash_password("Admin123!"),
                role=UserRole.ADMIN,
            )
            db.add(admin)

        doc_user = db.execute(select(User).filter_by(email="dr.watson@clinicflow.com")).scalar_one_or_none()
        if not doc_user:
            doc_user = User(
                email="dr.watson@clinicflow.com",
                full_name="Dr. Serhat Kutlu",
                phone_number="05552223344",
                hashed_password=hash_password("Doctor123!"),
                role=UserRole.DOCTOR,
            )
            db.add(doc_user)
            db.commit()
            db.refresh(doc_user)

            # Doktor Profili
            doc_profile = Doctor(
                user_id=doc_user.id,
                specialty="Kardiyoloji",
                room_number="A-101",
                working_start="09:00",
                working_end="17:00",
            )
            db.add(doc_profile)

        patient = db.execute(select(User).filter_by(email="hasta@clinicflow.com")).scalar_one_or_none()
        if not patient:
            patient = User(
                email="hasta@clinicflow.com",
                full_name="Ahmet Yilmaz",
                phone_number="05553334455",
                hashed_password=hash_password("Hasta123!"),
                role=UserRole.PATIENT,
            )
            db.add(patient)

        db.commit()
        print("Test kullanicilari (Admin, Doktor, Hasta) basariyla eklendi!")

    finally:
        db.close()


if __name__ == "__main__":
    seed()