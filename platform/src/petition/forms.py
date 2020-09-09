# -*- coding: utf-8 -*-

from django import forms
from . import models


class PetitionerForm(forms.Form):
    name = forms.CharField(label="Full name")
    aliases = forms.CharField(label="Aliases, comma separated")
    dob = forms.DateField(label="Date of birth")
    ssn = forms.CharField(label="Social security number")

    street1 = forms.CharField(label="Address")
    street2 = forms.CharField(label="Address line 2", required=False)
    city = forms.CharField(label="City")
    state = forms.CharField(label="State", max_length=3)
    zipcode = forms.CharField(label="Zip", max_length=11)

    def get_address(self):
        """Produce the Address object described by this form"""
        data = self.cleaned_data

        street2 = data.get("street2", None)

        if street2 is not None and street2.strip() == "":
            street2 = None

        return models.Address(
            data["street1"], data["city"], data["state"], data["zipcode"],
            street2=street2)

    def get_petitioner(self):
        """Produce the Petitioner described by this form"""
        data = self.cleaned_data
        aliases = data.get("aliases", "").split(",")

        return models.Petitioner(
            data["name"], aliases, data["dob"], data["ssn"],
            self.get_address())


class PetitionForm(PetitionerForm):
    date = forms.DateField(label="Petition date")
    petition_type = forms.ChoiceField(
        label="Petition type", choices=[(c.name, c.value) for c in
                                        models.PetitionType])
    otn = forms.CharField(label="OTN")
    dc = forms.CharField(label="DC")
    arrest_date = forms.DateField(label="Arrest date")
    arrest_officer = forms.CharField(label="Arresting officer")
    disposition = forms.CharField(label="Disposition")
    judge = forms.CharField(label="Judge")

    docket_id = forms.CharField(label="Docket ID")
    restitution_total = forms.FloatField(label="Restitition total")
    restitution_paid = forms.FloatField(label="Restitition paid")

    def get_docket_id(self):
        data = self.cleaned_data
        return models.DocketId.from_dict(data["docket_id"])

    def get_restitution(self):
        data = self.cleaned_data
        return models.Restitution(
            data["restitution_total"], data["restitution_paid"])

    def get_petition(self):
        data = self.cleaned_data
        return models.Petition(
            data["date"], models.PetitionType[data["petition_type"]],
            data["otn"], data["dc"], data["arrest_date"],
            data["arrest_officer"], data["disposition"], data["judge"])
