import re

import pytest
from django.test import TestCase
from petition import models
from petition import views

from docket_parser import test_data_path

# Current doc template will not support new line characters.
# A utility function replaces new lines with the appropriate line break char
# for the template.
class TestAddressFormatting(TestCase): 
    """Check that the petition helpers work"""

    def test_format_address_for_parser(self):
        address = models.Address(
            "street 1",
            "city",
            "PA",
            "12345"
        )
        res = views.format_address_for_template(address)
        self.assertEqual(res, "street 1<w:br/>city, PA 12345")
    
    def test_address1_and_address2_replace_new_lines(self):
        address = models.Address(
            "street 1",
            "city",
            "PA",
            "12345",
            "street 2"
        )
        res = views.format_address_for_template(address)
        self.assertEqual(res, "street 1<w:br/>street 2<w:br/>city, PA 12345")

    def test_address_with_extra_new_lines_are_also_formatted(self):
        address = models.Address(
            "street 1\n",
            "city\n",
            "PA\r",
            "12345",
            "street 2"
        )
        res = views.format_address_for_template(address)
        self.assertEqual(res, "street 1<w:br/>street 2<w:br/>city<w:br/>, PA<w:br/> 12345")

    def test_address_with_multiple_sequential_new_lines_gets_formatted_to_one_new_line(self):
        address = models.Address(
            "street 1\n\r\n\r\n\r\n\r",
            "city\n\n\n\n",
            "PA\n\r",
            "12345",
            "street 2"
        )
        res = views.format_address_for_template(address)
        self.assertEqual(res, "street 1<w:br/>street 2<w:br/>city<w:br/>, PA<w:br/> 12345")

    def test_address_is_none_returns_empty_string(self):
        res = views.format_address_for_template(None)
        self.assertEqual(res, '')
