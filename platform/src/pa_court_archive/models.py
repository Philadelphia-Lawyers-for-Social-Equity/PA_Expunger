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


class StatuteType(models.TextChoices):
    ORDINANCE = "O", gettext("Ordinance")
    STATUTE = "S", gettext("Statute")


class Arrestee(models.Model):
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["last_name"],
                condition=models.Q(first_name__isnull=True),
                name="unique_lastname_per_null_firstname"),
            models.UniqueConstraint(
                fields=["last_name", "first_name"],
                condition=(models.Q(middle_name__isnull=True) & models.Q(birth_date__isnull=True)),
                name="unique_lastname_firstname_per_null_middlename_null_birthdate"),
            models.UniqueConstraint(
                fields=["last_name", "first_name", "birth_date"],
                condition=models.Q(middle_name__isnull=True),
                name="unique_lastname_firstname_birthdate_per_null_middlename"),
            models.UniqueConstraint(
                fields=["last_name", "first_name", "middle_name"],
                condition=models.Q(birth_date__isnull=True),
                name="unique_fullname_per_null_birthdate"),
            models.UniqueConstraint(
                fields=["first_name", "last_name", "middle_name", "birth_date"],
                name="unique_arrestee")
        ]
        indexes = [
            models.Index(fields=["last_name", "first_name", "middle_name"]),
            models.Index(fields=["birth_date"])
        ]

    first_name = models.TextField(null=True)
    last_name = models.TextField()
    middle_name = models.TextField(null=True)
    gender_code = models.CharField(max_length=1, choices=GenderCode.choices, null=True)
    race_code = models.CharField(max_length=20, choices=RaceCode.choices, null=True)
    birth_date = models.DateField(null=True)

    def __str__(self):
        return "Arrestee <first_name: %s, last_name: %s>" % (
            str(self.first_name), str(self.last_name))


class Case(models.Model):
    class Meta:
        indexes = [models.Index(fields=["otn"])]

    otn = models.TextField(unique=True, null=False)
    filed_date = models.DateField(null=True)
    city = models.TextField(null=True)
    county = models.TextField(null=True)
    state = models.CharField(max_length=2, null=True)
    zip = models.CharField(max_length=10, null=True)
    disposition = models.TextField(null=True)
    disposition_date = models.DateField(null=True)
    disposing_judge = models.TextField(null=True)
    arrestees = models.ManyToManyField(Arrestee)

    def __str__(self):
        return "Case <otn: %s>" % self.otn


class Docket(models.Model):
    class Meta:
        indexes = [models.Index(fields=["docket_number"])]

    docket_number = models.TextField(unique=True, null=False)
    case = models.ForeignKey(Case, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return "Docket <docket_number: %s>" % self.docket_number


class Offense(models.Model):
    class Meta:
        indexes = [models.Index(fields=["docket"])]

    disposition = models.TextField(null=True)
    date = models.DateField(null=True)
    disposition_date = models.DateField(null=True)
    description = models.TextField(null=False)
    originating_sequence = models.IntegerField(null=True)

    statute_type = models.CharField(max_length=1, choices=StatuteType.choices, null=True)
    statute_title = models.TextField(null=True)
    statute_section = models.TextField(null=True)
    statute_subsection = models.TextField(null=True)
    inchoate_statute_title = models.TextField(null=True)
    inchoate_statute_section = models.TextField(null=True)
    inchoate_statute_subsection = models.TextField(null=True)

    grade = models.CharField(max_length=2, null=True)
    docket = models.ForeignKey(Docket, on_delete=models.CASCADE, null=False)

    def __str__(self):
        return "Offense <description: %s>" % self.description
