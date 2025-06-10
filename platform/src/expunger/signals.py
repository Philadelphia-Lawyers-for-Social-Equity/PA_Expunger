"""
signals.py

This module contains signal handlers for the Django application. 
Signals allow decoupled components to respond to application events.

Django Documentation on Signals:
https://docs.djangoproject.com/en/5.1/topics/signals/
"""
import os
import logging
from django.dispatch import receiver
from django.db.models.signals import post_migrate
from django.contrib.auth.models import User
from expunger.models import Attorney
from expunger.models import ExpungerProfile 

logger = logging.getLogger("django")

@receiver(post_migrate)
def create_default_atttorney(sender, **kwargs):
    # Initialization code to create default attorny if in development mode
    if (os.getenv("ENVIRONMENT") == "DEV"):
        if not Attorney.objects.exists():
            try:
                logger.info("Creating default attorney for plse user")
                plse_user = User.objects.get(username='plse')
                plse_user.first_name = "PLSE"
                plse_user.save()
                plse_attorney = Attorney.objects.create(user=plse_user, bar="TEST_BAR")
            except:
                logger.error("Failed to initialize plse attorney development data")


        
        