# -*- coding: UTF-8 -*-
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "oms_server.settings")

application = get_wsgi_application()
