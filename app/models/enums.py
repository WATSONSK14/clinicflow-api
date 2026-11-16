import enum

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    DOCTOR = "doctor"
    PATIENT = "patient"


class AppointmentStatus(str, enum.Enum):
    SCHEDULED = "scheduled"  # Randevu alındı, bekleniyor
    COMPLETED = "completed"  # Muayene bitti
    CANCELLED = "cancelled"  # İptal edildi