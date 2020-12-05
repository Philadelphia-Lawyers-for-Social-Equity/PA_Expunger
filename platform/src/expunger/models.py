# -*- coding: utf-8 -*-

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
        return "Address(street1=%s, street2=%s, city=%s, state=%s," \
               "zipcode=%s)" % (self.street1, self.street2, self.city,
                                self.state, self.zipcode)

    def __str__(self):
        if self.street2 is not None:
            return "%s\n%s\n%s, %s %s" % (
                self.street1, self.street2, self.city, self.state,
                self.zipcode)

        return "%s\n%s, %s %s" % (
            self.street1, self.city, self.state, self.zipcode)


class Organization(models.Model):
    name = models.CharField(max_length=128)
    address = models.ForeignKey(Address, on_delete=models.CASCADE)
    phone = models.CharField(max_length=32)

    def __repr__(self):
        return "Organization(name=%s, address=%s, phone=%s" % (
            self.name, self.address, self.phone)

    def __str__(self):
        return self.name


class Attorney(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE)
    bar = models.CharField(max_length=32)

    def __repr__(self):
        return "Attorney(user=%s, bar=%s" % (self.user, self.bar)

    def __str__(self):
        return "%s %s" % (self.user.first_name, self.user.last_name)


class ExpungerProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE)
    attorney = models.ForeignKey(Attorney, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)

    def __repr__(self):
        return "ExpungerProfile(user=%s, attorney=%s, organization=%s)" % (
            self.user, self.attorney, self.organization)

class DocketMetadata(models.Model):
    external_mysql_id = models.TextField(unique=True)
    county_name = models.TextField()
    docket_number = models.TextField(unique=True)
    filed_date = models.TextField()
    last_name = models.TextField()
    first_name = models.TextField()

    def __str__(self):
        return "%s: %s %s" % (self.docket_number, self.first_name, self.last_name)