import pytest
from django.test import TestCase
from petition import models

class TestPetitionerFromDict(TestCase):
    """Check that the helpers for petitioners work"""

    @classmethod
    def setUpClass(cls, *args, **kwargs):
        super().setUpClass(*args, **kwargs)
        cls.base_petitioner_model = {
            "name": "John Doe",
            "dob": "1900-01-01",
            "ssn": "111-11-1111",
            "address": {
                "street1": "100 Chestnut St",
                "city": "Philadelphia",
                "state": "PA",
                "zipcode": "12345"
            }
        }

    def test_no_aliases(self):
        petitioner_model = self.base_petitioner_model.copy()
        petitioner = models.Petitioner.from_dict(petitioner_model)
        self.assertEqual(petitioner.aliases, [])

    def test_none_aliases(self):
        petitioner_model = self.base_petitioner_model.copy()
        petitioner_model["aliases"] = None
        petitioner = models.Petitioner.from_dict(petitioner_model)
        self.assertEqual(petitioner.aliases, [])

    def test_empty_list_aliases(self):
        petitioner_model = self.base_petitioner_model.copy()
        petitioner_model["aliases"] = []
        petitioner = models.Petitioner.from_dict(petitioner_model)
        self.assertEqual(petitioner.aliases, [])

    def test_list_aliases(self):
        petitioner_model = self.base_petitioner_model.copy()
        test_alias_list = ["First Alias"]
        petitioner_model["aliases"] = test_alias_list
        petitioner = models.Petitioner.from_dict(petitioner_model)
        self.assertEqual(petitioner.aliases, test_alias_list)

    def test_invalid_aliases(self):
        petitioner_model = self.base_petitioner_model.copy()

        invalid_aliases = [
            "1",
            1,
            [1, 1],
            [1, "2"],
            ["1", "2", ["3", "4"]]
        ]

        for alias in invalid_aliases:
            petitioner_model["aliases"] = alias
            self.assertRaises(TypeError, models.Petitioner.from_dict, petitioner_model)
