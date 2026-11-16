from app.models import Appointment
from datetime import date, timedelta

def test_create_appointment_success(client, patient_token, test_doctor, test_patient) -> None:
    doctor = test_doctor()
    patient = test_patient()

    headers = {"Authorization": f"Bearer {patient_token(patient)}"}

    response = client.post(
        "/appointments",
        json={
            "doctor_id":doctor.id,
            "appointment_date": date.today().strftime("%Y-%m-%d"),
            "slot_id":"5",
            "notes":"Randevu Test",
        },
        headers=headers,
    )

    assert response.status_code == 201


def test_create_appointment_past_date_fails(client, patient_token, test_doctor, test_patient) -> None:
    doctor = test_doctor()
    patient = test_patient()

    headers = {"Authorization": f"Bearer {patient_token(patient)}"}

    response = client.post(
        "/appointments",
        json={
            "doctor_id":doctor.id,
            "appointment_date":"2025-11-11",
            "slot_id":"5",
            "notes":"Randevu Test",
        },
        headers=headers,
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Geçmiş bir tarihe randevu alınamaz."



def test_create_appointment_outside_working_hours_fails(client, patient_token, test_doctor, test_patient) -> None:
    doctor = test_doctor()
    patient = test_patient()

    headers = {"Authorization": f"Bearer {patient_token(patient)}"}

    response = client.post(
        "/appointments",
        json={
            "doctor_id":doctor.id,
            "appointment_date": date.today().strftime("%Y-%m-%d"),
            "slot_id":"1",
            "notes":"Randevu Test",
        },
        headers=headers,
    )

    assert response.status_code == 400
    assert response.json()["detail"] == f"Randevu saati doktorun çalışma saatleri ({doctor.working_start} - {doctor.working_end}) içinde olmalıdır."



def test_create_appointment_double_booking_same_doctor_fails(client, patient_token, test_doctor, test_patient) -> None:
    doctor = test_doctor()
    patient = test_patient()
    patient_2 = test_patient(email="testpatient2@gmail.com")

    headers = {"Authorization": f"Bearer {patient_token(patient)}"}
    headers_2 = {"Authorization": f"Bearer {patient_token(patient_2)}"}

    response = client.post(
        "/appointments",
        json={
            "doctor_id":doctor.id,
            "appointment_date": date.today().strftime("%Y-%m-%d"),
            "slot_id":"5",
            "notes":"Randevu Test",
        },
        headers=headers,
    )

    response_2 = client.post(
        "/appointments",
        json={
            "doctor_id":doctor.id,
            "appointment_date": date.today().strftime("%Y-%m-%d"),
            "slot_id":"5",
            "notes":"Randevu Test2",
        },
        headers=headers_2,
    )


    assert response.status_code == 201
    assert response_2.status_code == 409

    assert response_2.json()["detail"] == "Bu randevu saati doludur, lütfen başka bir saat seçiniz."


def test_create_appointment_same_specialty_fails(client, patient_token, test_doctor, test_patient) -> None:
    doctor = test_doctor()
    patient = test_patient()

    headers = {"Authorization": f"Bearer {patient_token(patient)}"}

    
    response = client.post(
        "/appointments",
        json={
            "doctor_id":doctor.id,
            "appointment_date": date.today().strftime("%Y-%m-%d"),
            "slot_id":"5",
            "notes":"Randevu Test",
        },
        headers=headers,
    )

    response_2 = client.post(
        "/appointments",
        json={
            "doctor_id":doctor.id,
            "appointment_date": (date.today() + timedelta(days=1)).strftime("%Y-%m-%d"),
            "slot_id":"5",
            "notes":"Randevu Test",
        },
        headers=headers,
    )


    assert response.status_code == 201
    assert response_2.status_code == 400
    assert response_2.json()["detail"] == "Aynı Branştan Aynı Anda 1 Randevu Alabilirsiniz."


def test_create_appointment_same_timeslot_different_doctor_fails(client, patient_token, test_doctor, test_patient) -> None:
    doctor = test_doctor()
    doctor_2 = test_doctor(email="doctor2@test.com", specialty="Göz Hastalıkları")
    patient = test_patient()

    headers = {"Authorization": f"Bearer {patient_token(patient)}"}



    response = client.post(
        "/appointments",
        json={
            "doctor_id":doctor.id,
            "appointment_date": date.today().strftime("%Y-%m-%d"),
            "slot_id":"5",
            "notes":"Randevu Test",
        },
        headers=headers,
    )

    response_2 = client.post(
        "/appointments",
        json={
            "doctor_id":doctor_2.id,
            "appointment_date": date.today().strftime("%Y-%m-%d"),
            "slot_id":"5",
            "notes":"Randevu Test",
        },
        headers=headers,
    )


    assert response.status_code == 201
    assert response_2.status_code == 400
    assert response_2.json()["detail"] == "Bu Tarih ve Saatte Zaten Bir Randevunuz Var."


def test_create_appointment_max_active_quota_fails(client, patient_token, test_doctor, test_patient) -> None:
    doctor = test_doctor()
    doctor_2 = test_doctor(email="doctor2@test.com", specialty="Göz Hastalıkları")
    doctor_3 = test_doctor(email="doctor3@test.com", specialty="Ortopedi")
    doctor_4 = test_doctor(email="doctor4@test.com", specialty="Sinir Hastalıkları")

    patient = test_patient()

    headers = {"Authorization": f"Bearer {patient_token(patient)}"}

    response = client.post(
        "/appointments",
        json={
            "doctor_id":doctor.id,
            "appointment_date": date.today().strftime("%Y-%m-%d"),
            "slot_id":"5",
            "notes":"Randevu Test",
        },
        headers=headers,
    )

    response_2 = client.post(
        "/appointments",
        json={
            "doctor_id":doctor_2.id,
            "appointment_date": date.today().strftime("%Y-%m-%d"),
            "slot_id":"6",
            "notes":"Randevu Test",
        },
        headers=headers,
    )

    response_3 = client.post(
        "/appointments",
        json={
            "doctor_id":doctor_3.id,
            "appointment_date": date.today().strftime("%Y-%m-%d"),
            "slot_id":"7",
            "notes":"Randevu Test",
        },
        headers=headers,
    )

    response_4 = client.post(
        "/appointments",
        json={
            "doctor_id":doctor_4.id,
            "appointment_date": date.today().strftime("%Y-%m-%d"),
            "slot_id":"8",
            "notes":"Randevu Test",
        },
        headers=headers,
    )

    assert response.status_code == 201
    assert response_2.status_code == 201
    assert response_3.status_code == 201
    assert response_4.status_code == 400

    assert response_4.json()["detail"] == "Bir Kullanıcı Aynı Anda Sadece 3 Randevu Alabilir."


def test_create_appointment_non_existent_doctor_fails(client, patient_token, test_patient) -> None:

    patient = test_patient()
    headers = {"Authorization": f"Bearer {patient_token(patient)}"}

    response = client.post(
        "/appointments",
        json={
            "doctor_id":"1",
            "appointment_date": date.today().strftime("%Y-%m-%d"),
            "slot_id":"5",
            "notes":"Randevu Test",
        },
        headers=headers,
    )


    assert response.status_code == 404
    assert response.json()["detail"] == "Seçilen doktor bulunamadı."


def test_create_appointment_invalid_slot_fails(client, patient_token, test_doctor, test_patient) -> None:
    doctor = test_doctor()
    patient = test_patient()

    headers = {"Authorization": f"Bearer {patient_token(patient)}"}

    response = client.post(
        "/appointments",
        json={
            "doctor_id":doctor.id,
            "appointment_date": date.today().strftime("%Y-%m-%d"),
            "slot_id":"45",
            "notes":"Randevu Test",
        },
        headers=headers,
    )


    assert response.status_code == 404
    assert response.json()["detail"] == "Geçersiz randevu saati dilimi."


def test_cancel_appointment_success(client, patient_token, test_doctor, test_patient) -> None:
    doctor = test_doctor()
    patient = test_patient()

    headers = {"Authorization": f"Bearer {patient_token(patient)}"}

    
    response = client.post(
        "/appointments",
        json={
            "doctor_id":doctor.id,
            "appointment_date": date.today().strftime("%Y-%m-%d"),
            "slot_id":"5",
            "notes":"Randevu Test",
        },
        headers=headers,
    )

    appointment_id = response.json()["id"]

    cancel_response = client.patch(
        f"/appointments/{appointment_id}/cancel",
        headers=headers
    )

    assert response.status_code == 201
    assert cancel_response.status_code == 200

    assert cancel_response.json()["status"] == "cancelled"



def test_rebook_cancelled_appointment_slot_success(client, patient_token, test_doctor, test_patient) -> None:
    doctor = test_doctor()
    patient = test_patient()

    headers = {"Authorization": f"Bearer {patient_token(patient)}"}

    
    response = client.post(
        "/appointments",
        json={
            "doctor_id":doctor.id,
            "appointment_date": date.today().strftime("%Y-%m-%d"),
            "slot_id":"5",
            "notes":"Randevu Test",
        },
        headers=headers,
    )

    appointment_id = response.json()["id"]

    cancel_response = client.patch(
        f"/appointments/{appointment_id}/cancel",
        headers=headers
    )

    response_2 = client.post(
        "/appointments",
        json={
            "doctor_id":doctor.id,
            "appointment_date": date.today().strftime("%Y-%m-%d"),
            "slot_id":"5",
            "notes":"Randevu Test",
        },
        headers=headers,
    )

    assert response.status_code == 201
    assert response_2.status_code == 201
    assert cancel_response.status_code == 200

    assert cancel_response.json()["status"] == "cancelled"
    assert response_2.json()["status"] == "scheduled"



def test_cancel_already_cancelled_appointment_fails(client, patient_token, test_doctor, test_patient) -> None:
    doctor = test_doctor()
    patient = test_patient()

    headers = {"Authorization": f"Bearer {patient_token(patient)}"}

    
    response = client.post(
        "/appointments",
        json={
            "doctor_id":doctor.id,
            "appointment_date": date.today().strftime("%Y-%m-%d"),
            "slot_id":"5",
            "notes":"Randevu Test",
        },
        headers=headers,
    )

    appointment_id = response.json()["id"]

    cancel_response = client.patch(
        f"/appointments/{appointment_id}/cancel",
        headers=headers
    )


    cancel_response_2 = client.patch(
        f"/appointments/{appointment_id}/cancel",
        headers=headers
    )

    assert response.status_code == 201
    assert cancel_response.status_code == 200
    assert cancel_response_2.status_code == 400

    assert cancel_response.json()["status"] == "cancelled"
    assert cancel_response_2.json()["detail"] == "Bu randevu zaten iptal edilmiş."


def test_cancel_completed_appointment_fails(client, patient_token, test_doctor, test_patient, db) -> None:
    doctor = test_doctor()
    patient = test_patient()

    headers = {"Authorization": f"Bearer {patient_token(patient)}"}

    
    response = client.post(
        "/appointments",
        json={
            "doctor_id":doctor.id,
            "appointment_date": date.today().strftime("%Y-%m-%d"),
            "slot_id":"5",
            "notes":"Randevu Test",
        },
        headers=headers,
    )

    appointment_id = response.json()["id"]
    appointment = db.get(Appointment, appointment_id)

    appointment.status = "COMPLETED"
    db.commit()
    db.refresh(appointment)

    cancel_response = client.patch(
        f"/appointments/{appointment_id}/cancel",
        headers=headers
    )

    assert cancel_response.status_code == 400
    assert cancel_response.json()["detail"] == "Bu randevu iptal edilemez."

def test_cancel_non_existent_appointment_fails(client, patient_token, test_patient) -> None:
    patient = test_patient()

    headers = {"Authorization": f"Bearer {patient_token(patient)}"}


    cancel_response = client.patch(
        "/appointments/1/cancel",
        headers=headers
    )

    assert cancel_response.status_code == 404
    assert cancel_response.json()["detail"] == "Randevu bulunamadı!"


def test_cancel_other_patient_appointment_forbidden(client, patient_token, test_doctor, test_patient) -> None:
    doctor = test_doctor()
    patient = test_patient()
    patient_2 = test_patient(email="test2@gmail.com")

    headers = {"Authorization": f"Bearer {patient_token(patient)}"}
    headers_2 = {"Authorization": f"Bearer {patient_token(patient_2)}"}

    
    response = client.post(
        "/appointments",
        json={
            "doctor_id":doctor.id,
            "appointment_date": date.today().strftime("%Y-%m-%d"),
            "slot_id":"5",
            "notes":"Randevu Test",
        },
        headers=headers,
    )

    appointment_id = response.json()["id"]

    cancel_response = client.patch(
        f"/appointments/{appointment_id}/cancel",
        headers=headers_2
    )

    assert response.status_code == 201
    assert cancel_response.status_code == 403
    assert cancel_response.json()["detail"] == "Bu randevuyu iptal etme yetkiniz yok!"