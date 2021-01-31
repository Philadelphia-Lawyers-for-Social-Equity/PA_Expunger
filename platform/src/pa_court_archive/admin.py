# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import Arrestee, Case, Docket, Offense

admin.site.register(Arrestee)
admin.site.register(Case)
admin.site.register(Docket)
admin.site.register(Offense)
