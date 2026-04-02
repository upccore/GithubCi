import pytest
from app import create_app
from models import db, Parking, ClientParking
from factories import ClientFactory
from datetime import datetime, timedelta
from routes import init_routes


def pytest_configure(config):
    config.addinivalue_line("markers", "parking: тесты заезда и выезда")


@pytest.fixture
def app():
    app = create_app()
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['TESTING'] = True

    init_routes(app)

    with app.app_context():
        db.create_all()

        client = ClientFactory(
            name='Иван',
            surname='Иванов',
            credit_card='1234-5678-9012-3456',
            car_number='A123BC'
        )
        db.session.add(client)

        parking = Parking(
            address='ул. Тестовая, 1',
            opened=True,
            count_places=10,
            count_available_places=10
        )
        db.session.add(parking)

        client_parking = ClientParking(
            client_id=1,
            parking_id=1,
            time_in=datetime.now() - timedelta(hours=2),
            time_out=datetime.now()
        )
        db.session.add(client_parking)

        db.session.commit()

        yield app

        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def db_session(app):
    with app.app_context():
        yield db.session
