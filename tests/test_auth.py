def test_register_user_success(client) -> None:

    user = {
        "email":"testemail@gmail.com",
        "full_name":"Jhon Watson",
        "phone_number":"05555555555",
        "password":"TESTpw12345",
    }

    response = client.post(
        "/auth/register",
        json=user,
    )

    assert response.status_code == 201
    assert response.json()["email"] == user["email"]
    assert response.json()["full_name"] == user["full_name"]
    assert response.json()["role"] == "patient"
    assert "hashed_password" not in response.json()
    assert "password" not in response.json()


def test_register_duplicate_email_fails(client, test_patient) -> None:
    patient = test_patient()

    duplicated_user = {
        "email": patient.email,
        "full_name": "test_2",
        "phone_number": "05554566515",
        "password": "TESTPW123456",
    }

    response = client.post(
        "/auth/register",
        json=duplicated_user
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Bu e-posta adresi zaten kayıtlı!"


def test_login_success(client, test_patient) -> None:
    patient = test_patient()

    response = client.post(
        "/auth/login",
        data={
            "username":patient.email,
            "password":"Pass123!",
        }
    )

    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_login_wrong_password_fails(client, test_patient) -> None:
    patient = test_patient()

    response = client.post(
        "/auth/login",
        data={
            "username":patient.email,
            "password":"WrongPw!",
        }
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Hatalı e-posta veya şifre!"
    assert "access_token" not in response.json()


def test_get_current_user_me_success(client, patient_token, test_patient) -> None:
    patient = test_patient()
    headers = {"Authorization": f"Bearer {patient_token(patient)}"}

    response = client.post(
        "/auth/login",
        data={
            "username":patient.email,
            "password":"Pass123!",
        }
    )

    response_2 = client.get(
        "/auth/me",
        headers=headers
    )

    assert response.status_code == 200
    assert response_2.status_code == 200

    assert response_2.json()["email"] == patient.email
    assert response_2.json()["full_name"] == patient.full_name
    assert response_2.json()["id"] == patient.id
    assert response_2.json()["phone_number"] == patient.phone_number