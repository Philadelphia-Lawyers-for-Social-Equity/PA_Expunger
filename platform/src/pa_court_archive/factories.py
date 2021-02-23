# -*- coding: utf-8 -*-
import random

import factory
from factory.fuzzy import FuzzyAttribute, FuzzyChoice

from . import models


class ArresteeFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = models.Arrestee

    last_name = factory.Faker("last_name")
    first_name = factory.Faker("first_name")
    middle_name = factory.Faker("first_name")

    gender_code = FuzzyChoice(models.GenderCode.values)
    race_code = FuzzyChoice(models.RaceCode.values)
    birth_date = factory.Faker("date")


class CaseFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = models.Case

    otn = factory.Sequence(lambda n: "N%07d" % n)
    filed_date = factory.Faker("date")
    city = "Philadelphia"
    county = "Philadelphia"
    state = "PA"
    zip = FuzzyAttribute(lambda: "1910" + str(random.randint(1, 9)))
    disposition = FuzzyChoice(
        ["Nolle Prossed", "Dismissed", "Withdrawn", "Guilty", "Not Guilty"])
    disposition_date = factory.Faker("date")
    disposing_judge = factory.Faker("name")

    dockets = factory.RelatedFactoryList("pa_court_archive.factories.DocketFactory", factory_related_name="case", size=2)

    @factory.post_generation
    def arrestees(self, create, extracted, **kwargs):
        self.arrestees.add(ArresteeFactory())


class DocketFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = models.Docket

    docket_number = factory.Sequence(lambda n: "MC-51-CR-100%04d-2020" % n)
    case = factory.SubFactory("pa_court_archive.factories.CaseFactory")

    offenses = factory.RelatedFactoryList("pa_court_archive.factories.OffenseFactory", factory_related_name="docket", size=3)


class OffenseFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = models.Offense

    disposition = FuzzyChoice(["Nolle Prossed", "Dismissed", "Withdrawn", "Guilty", "Not Guilty"])
    date = factory.Faker("date")
    disposition_date = factory.Faker("date")
    description = FuzzyChoice(["Escape", "Loitering", "Criminal Mischief"])
    originating_sequence = FuzzyAttribute(lambda: random.randint(1, 10))

    statute_type = FuzzyChoice(models.StatuteType.values)
    statute_title = FuzzyChoice(["LO", "18", "43", "75", "35", "CO"])
    statute_section = FuzzyAttribute(lambda: str(random.randint(1000, 9999)))
    statute_subsection = FuzzyChoice(["2", "A2i", "A3-25", "A1IV", "A19", "B1", "A1**", "D1**"])

    inchoate_statute_title = FuzzyChoice(["18", "75", "0"])
    inchoate_statute_section = FuzzyChoice(["901", "902", "903", "1575", "0"])
    inchoate_statute_subsection = FuzzyChoice(["A", "A1", "A2", "B", "0", None])

    grade = FuzzyChoice(["S", "F3", "M"])
    docket = factory.SubFactory("pa_court_archive.factories.DocketFactory")
