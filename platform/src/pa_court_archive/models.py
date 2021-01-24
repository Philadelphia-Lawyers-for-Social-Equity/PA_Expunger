# -*- coding: utf-8 -*-

from django.db import models

"""
Provide an interface for the PA Court Data that PLSE purchased.
"""


class PaRecord(models.Model):
    external_mysql_id = models.TextField(unique=True)
    county_name = models.TextField(null=True)
    docket_number = models.TextField(null=True)
    filed_date = models.TextField(null=True)
    last_name = models.TextField(null=True)
    first_name = models.TextField(null=True)
    middle_name = models.TextField(null=True)
    city = models.TextField(null=True)
    state = models.TextField(null=True)
    zipcode = models.TextField(null=True)
    offense_tracking_number = models.TextField(null=True)
    gender_code = models.TextField(null=True)
    race_code = models.TextField(null=True)
    birthdate = models.TextField(null=True)
    originating_offense_sequence = models.TextField(null=True)
    statute_type = models.TextField(null=True)
    statute_title = models.TextField(null=True)
    statute_section = models.TextField(null=True)
    statute_subsection = models.TextField(null=True)
    inchoate_statute_title = models.TextField(null=True)
    inchoate_statute_section = models.TextField(null=True)
    inchoate_statute_subsection = models.TextField(null=True)
    offense_disposition = models.TextField(null=True)
    offense_date = models.TextField(null=True)
    offense_disposition_date = models.TextField(null=True)
    offense_description = models.TextField(null=True)
    case_disposition = models.TextField(null=True)
    case_disposition_date = models.TextField(null=True)
    offense_grade = models.TextField(null=True)
    disposing_judge = models.TextField(null=True)

    def __str__(self):
        return "%s: %s %s" % (self.docket_number, self.first_name, self.last_name)
