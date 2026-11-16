from datetime import date


def test_get_doctors_list_success(client, test_doctor) -> None:
    doctor = test_doctor()

    response = client.get(
        "/doctors/",
    )

    assert response.status_code == 200
    assert len(response.json()) >= 1

    assert response.json()[0]["specialty"] == doctor.specialty
    assert response.json()[0]["room_number"] == doctor.room_number
    assert response.json()[0]["working_start"] == doctor.working_start
    assert response.json()[0]["working_end"] == doctor.working_end


def test_get_doctor_available_slots_success(client, patient_token, test_doctor, test_patient) -> None:
    doctor = test_doctor(working_start="08.00", working_end="18:00")
    patient = test_patient()

    headers = {"Authorization": f"Bearer {patient_token(patient)}"}

    today = date.today().strftime("%Y-%m-%d")

    response = client.post(
        "/appointments",
        json={
            "doctor_id":doctor.id,
            "appointment_date": today,
            "slot_id":"5",
            "notes":"Randevu Test",
        },
        headers=headers,
    )

    response_2 = client.get(
        f"/doctors/{doctor.id}/available-slots?appointment_date={today}",
    )

    data = response_2.json()

    assert response.status_code == 201
    assert response_2.status_code == 200

    assert len(data) == 20
    assert "id" in data[0]
    assert "start_time" in data[0]
    assert "end_time" in data[0]
    assert "is_available" in data[0]

    assert all(data[x]["is_available"] for x in range(len(data)) if x != 4) == True
    assert data[4]["is_available"] == False