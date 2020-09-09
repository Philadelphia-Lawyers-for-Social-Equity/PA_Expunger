# -*- coding: utf-8 -*-

from django.contrib import admin
from .models import Address, Organization, Attorney, ExpungerProfile

admin.site.register(Address)
admin.site.register(Organization)
admin.site.register(Attorney)
admin.site.register(ExpungerProfile)
