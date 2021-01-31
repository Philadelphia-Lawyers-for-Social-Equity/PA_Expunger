# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import gettext_lazy as gettext

"""
Provide an interface for the PA Court Data that PLSE purchased.
"""

class GenderCode(models.TextChoices):
    MALE = "M", gettext("Male")
    FEMALE = "F", gettext("Female")
    UNREPORTED = "U", gettext("Unknown/Unreported")

class RaceCode(models.TextChoices):
    WHITE = "WHITE", gettext("White")
    BLACK = "BLACK", gettext("Black")
    UNREPORTED = "UNREPORTED", gettext("Unknown/Unreported")
    ASIAN = "ASIAN", gettext("Asian")
    ASIAN_PACIFIC = "ASIANgettextPACIFIC", gettext("Asian/Pacific Islander")
    NATIVE = "NATIVE", gettext("Native American/Alaskan Native")
    BIRACIAL = "BIRACIAL", gettext("Bi-Racial")
    HAWAIIAN_PACIFIC = "HAWAIIAN_PACIFIC", gettext("Native Hawaiian/Pacific Islander")

class Arrestee(models.Model):
    class Meta:
        constraints = [models.UniqueConstraint(fields=["first_name", "last_name", "middle_name", "birth_date"], name="unique_arrestee")]
    
    first_name = models.TextField(null=True)
    last_name = models.TextField()
    middle_name = models.TextField(null=True)
    gender_code = models.CharField(max_length=1, choices=GenderCode.choices, null=True)
    race_code = models.CharField(max_length=16, choices=RaceCode.choices, null=True)
    birth_date = models.DateField(null=True)

class Case(models.Model):
    otn = models.TextField(unique=True, null=False)
    filed_date = models.DateField(null=True)
    city = models.TextField(null=True)
    county = models.TextField(null=True)
    state = models.CharField(max_length=2, null=True)
    zip = models.CharField(max_length= 10, null=True)
    disposition = models.TextField(null=True)
    disposition_date = models.DateField(null=True)
    disposing_judge = models.TextField(null=True)
    arrestees = models.ManyToManyField(Arrestee, null=True)

class Docket(models.Model):
    docket_number = models.TextField(unique=True, null=False)
    case = models.ForeignKey(Case, on_delete=models.CASCADE, null=True)

class Offense(models.Model):
    disposition = models.TextField(null=True)
    date = models.DateField(null=True)
    disposition_date = models.DateField(null=True)
    description = models.TextField(null=True)
    originating_sequence = models.IntegerField(null=True)
    statute_title = models.TextField(null=True)
    statute_section = models.TextField(null=True)
    statute_subsection = models.TextField(null=True)
    inchoate_statute_title = models.TextField(null=True)
    inchoate_statute_section = models.TextField(null=True)
    inchoate_statute_subsection = models.TextField(null=True)
    grade = models.CharField(max_length=2, null=True)
    docket = models.ForeignKey(Docket, on_delete=models.CASCADE, null=True)
