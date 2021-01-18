# -*- coding: utf-8 -*-
import random

import factory
from factory.fuzzy import FuzzyAttribute, FuzzyChoice

from . import models


class PaRecordFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = models.PaRecord

    external_mysql_id = FuzzyAttribute(lambda: str(random.randint(1, 10)))
    county_name = "Philadelphia"
    docket_number = "CP-51-CR-0504991-2004"
    filed_date = factory.Faker("date")
    last_name = factory.Faker("name")
    first_name = factory.Faker("name")
    middle_name = factory.Faker("name")
    city = "Philadelphia"
    state = "PA"
    zipcode = FuzzyAttribute(lambda: "1910" + str(random.randint(1, 9)))
    offense_tracking_number = "MC-51-CR-0436451-2004"
    gender_code = random.choice(["Male", "Female"])
    race_code = FuzzyChoice(["Black", "White"])
    birthdate = factory.Faker("date")
    originating_offense_sequence = FuzzyAttribute(
        lambda: str(random.randint(1, 10)))
    statute_type = FuzzyChoice(["Ordinance", "Statute"])
    statute_title = FuzzyChoice(["LO", "18", "43", "75", "35", "CO"])
    statute_section = FuzzyAttribute(lambda: str(random.randint(1000, 9999)))
    statute_subsection = FuzzyChoice(
        ["2", "A2i", "A3-25", "A1IV", "A19", "B1", "A1**", "D1**"])
    inchoate_statute_title = FuzzyChoice(["18", "75", "0", None])
    inchoate_statute_section = FuzzyChoice(
        ["901", "902", "903", "1575", "0", None])
    inchoate_statute_subsection = FuzzyChoice(["A", "A1", "A2", "B", "0", None])
    offense_disposition = FuzzyChoice(
        ["Nolle Prossed", "Dismissed", "Withdrawn", "Guilty", "Not Guilty"])
    offense_date = factory.Faker("date")
    offense_disposition_date = factory.Faker("date")
    offense_description = None
    case_disposition = factory.LazyAttribute(
        lambda obj: obj.offense_disposition)
    case_disposition_date = factory.Faker("date")
    offense_grade = None
    disposing_judge = factory.Faker("name")
