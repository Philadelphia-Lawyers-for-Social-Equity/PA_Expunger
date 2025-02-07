from datetime import date
import factory
import factory.fuzzy
from .models import Address, Petitioner, Court, CaseType, DocketId, \
    PetitionRatio, Petition, Fines, Charge


class AddressFactory(factory.Factory):
    class Meta:
        model = Address

    street1 = factory.Faker("street_address")
    city = factory.Faker("city")
    state = factory.Faker("state_abbr")
    zipcode = factory.Faker("zipcode")


class PetitionerFactory(factory.Factory):
    class Meta:
        model = Petitioner

    name = factory.Faker("name")
    aliases = []
    dob = factory.Faker("date_this_century")
    ssn = factory.Faker("ssn")
    address = factory.SubFactory(AddressFactory)


class DocketIdFactory(factory.Factory):
    class Meta:
        model = DocketId

    court = factory.fuzzy.FuzzyChoice(Court)
    case_type = factory.fuzzy.FuzzyChoice(CaseType)
    number = factory.fuzzy.FuzzyInteger(1, 9999999)
    year = factory.fuzzy.FuzzyInteger(1968, 2019)


class PetitionFactory(factory.Factory):
    class Meta:
        model = Petition

    complaint_date = date.today()
    arrest_date = date.today()
    date = date.today()
    ratio = factory.fuzzy.FuzzyChoice(PetitionRatio)
    otn = factory.fuzzy.FuzzyInteger(1000000, 9999999)
    judge = factory.Faker("name")


class FinesFactory(factory.Factory):
    class Meta:
        model = Fines

    total = factory.fuzzy.FuzzyInteger(500, 1000)
    paid = factory.fuzzy.FuzzyInteger(0, 499)

class ChargeFactory(factory.Factory):
    class Meta:
        model = Charge

    date = factory.Faker("date_this_century")
    statute = factory.Faker("numerify", text='## § #### §§ #')
    grade = factory.Faker("random_choices", elements=('S', 'M', 'M1', 'M2', 'M3', 'F', 'F1', 'F2', 'F3'), length=1)
    description = factory.Faker("text", max_nb_chars=40)
    disposition = factory.Faker("text", max_nb_chars=15)
