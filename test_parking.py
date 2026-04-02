import pytest
from models import Parking, ClientParking, Client
from factories import ClientFactory, ParkingFactory


@pytest.mark.parametrize("url", ["/clients", "/clients/1"])
def test_get_200(client, url):
    assert client.get(url).status_code == 200


def test_create_client(client):
    res = client.post("/clients", json={"name": "Петр", "surname": "Петров"})
    assert res.status_code == 201


def test_create_client_with_factory(client, db_session):
    count_before = db_session.query(Client).count()

    client_data = ClientFactory.build()
    res = client.post(
        "/clients",
        json={
            "name": client_data.name,
            "surname": client_data.surname,
            "credit_card": client_data.credit_card,
            "car_number": client_data.car_number,
        },
    )

    assert res.status_code == 201
    assert "id" in res.json

    count_after = db_session.query(Client).count()
    assert count_after == count_before + 1


def test_create_parking(client):
    res = client.post("/parkings", json={"address": "ул. Тест", "count_places": 10})
    assert res.status_code == 201


def test_create_parking_with_factory(client, db_session):
    count_before = db_session.query(Parking).count()

    parking_data = ParkingFactory.build()
    res = client.post(
        "/parkings",
        json={
            "address": parking_data.address,
            "count_places": parking_data.count_places,
        },
    )

    assert res.status_code == 201
    assert "id" in res.json

    count_after = db_session.query(Parking).count()
    assert count_after == count_before + 1


@pytest.mark.parking
def test_car_in(client, db_session):
    db_session.query(ClientParking).filter_by(client_id=1, parking_id=1).delete()
    db_session.commit()

    parking = db_session.get(Parking, 1)
    assert parking.opened == True

    before = parking.count_available_places

    res = client.post("/client_parkings", json={"client_id": 1, "parking_id": 1})
    assert res.status_code == 200

    db_session.refresh(parking)
    assert parking.count_available_places == before - 1


@pytest.mark.parking
def test_car_out(client, db_session):
    db_session.query(ClientParking).filter_by(client_id=1, parking_id=1).delete()
    db_session.commit()

    client.post("/client_parkings", json={"client_id": 1, "parking_id": 1})

    parking = db_session.get(Parking, 1)
    before = parking.count_available_places

    client_model = db_session.get(Client, 1)
    assert client_model.credit_card is not None

    res = client.delete("/client_parkings", json={"client_id": 1, "parking_id": 1})
    assert res.status_code == 200

    db_session.refresh(parking)
    assert parking.count_available_places == before + 1

    log = db_session.query(ClientParking).filter_by(client_id=1).first()
    assert log.time_out >= log.time_in
    assert "price" in res.json
