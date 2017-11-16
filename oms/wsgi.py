# -*- coding: UTF-8 -*-
"""
WSGI config for oms project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

env = os.environ.get("AIRCOS_ENV", "test")
print("xxxxxxxxxxxxxxxxxxxxxxx")
print(env)
if env == "product":
    os.environ["DJANGO_SETTINGS_MODULE"] = "oms.settings.product"
elif env == "test":
    os.environ["DJANGO_SETTINGS_MODULE"] = "oms.settings.test"
else:
    os.environ["DJANGO_SETTINGS_MODULE"] = "oms.settings.local"

application = get_wsgi_application()
