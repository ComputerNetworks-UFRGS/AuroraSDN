"""
WSGI config for Aurora project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/howto/deployment/wsgi/
"""

import sys
sys.path.append('/home/aurora/Aurora')

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Aurora.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
