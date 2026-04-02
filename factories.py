import factory
from faker import Faker

from models import Client, Parking

fake = Faker()


class ClientFactory(factory.Factory):
    class Meta:
        model = Client

    name = factory.Faker("first_name")
    surname = factory.Faker("last_name")
    credit_card = factory.Faker("credit_card_number")
    car_number = factory.Faker("license_plate")


class ParkingFactory(factory.Factory):
    class Meta:
        model = Parking

    address = factory.Faker("street_address")
    opened = factory.Faker("boolean")
    count_places = factory.Faker("random_int", min=1, max=100)
    count_available_places = factory.LazyAttribute(lambda obj: obj.count_places)
