from django.db import models
from django.conf import settings


class Address(models.Model):
    """Standard US Address"""
    street1 = models.CharField(max_length=128)
    street2 = models.CharField(max_length=128, null=True)
    city = models.CharField(max_length=128)
    state = models.CharField(max_length=2)
    zipcode = models.CharField(max_length=10)

    def __repr__(self):
        return f"Address(street1={self.street1}, street2={self.street2}, city={self.city}," \
               f" state={self.state}, zipcode={self.zipcode})"

    def __str__(self):
        if self.street2 is not None:
            return f"{self.street1}\n{self.street2}\n{self.city}, {self.state} {self.zipcode}"

        return f"{self.street1}\n{self.city}, {self.state} {self.zipcode}"


class Organization(models.Model):
    name = models.CharField(max_length=128)
    address = models.ForeignKey(Address, on_delete=models.CASCADE)
    phone = models.CharField(max_length=32)

    def __repr__(self):
        return f"Organization(name={self.name}, address={self.address}, phone={self.phone}"

    def __str__(self):
        return self.name


class Attorney(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE)
    bar = models.CharField(max_length=32)

    def __repr__(self):
        return f"Attorney(user={self.user}, bar={self.bar}"

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"


class ExpungerProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE)
    attorney = models.ForeignKey(Attorney, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)

    def __repr__(self):
        return f"ExpungerProfile(user={self.user}, attorney={self.attorney}, organization={self.organization})"
