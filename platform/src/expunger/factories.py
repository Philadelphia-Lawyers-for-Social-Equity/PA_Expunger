import random
import string
from django.contrib.auth import get_user_model

import factory
from . import models


def random_text(length):
    text = ""
    for _ in range(length):
        text += random.choice(string.ascii_lowercase)

    return text


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = get_user_model()

    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    email = factory.Faker("ascii_email")
    password = factory.LazyAttribute(lambda o: o.set_password(random_text(8)))

    @factory.lazy_attribute
    def username(self):
        return f"{self.first_name}-{self.last_name}"

    @factory.post_generation
    def password(obj, created, extracted, *args, **kwargs):

        if extracted is None:
            password = random_text(8)
        else:
            password = extracted

        obj.set_password(password)


class AddressFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Address

    street1 = factory.Faker("street_address")
    city = factory.Faker("city")
    state = factory.Faker("state_abbr")
    zipcode = factory.Faker("zipcode")


class OrganizationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Organization

    name = factory.Faker("company")
    phone = factory.Faker("phone_number")
    address = factory.SubFactory(AddressFactory)


class AttorneyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Attorney

    user = factory.SubFactory(UserFactory)
    bar = factory.LazyAttribute(lambda o: str(random.randint(100000, 999999)))


class ExpungerProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.ExpungerProfile

    user = factory.SubFactory(UserFactory)
    attorney = factory.SubFactory(AttorneyFactory)
    organization = factory.SubFactory(OrganizationFactory)
