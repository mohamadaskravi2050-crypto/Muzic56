"""
WSGI config for muzic56 project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'muzic56.settings')

application = get_wsgi_application()

#WSGI و ASGI هر دو interface (رابط) بین وب‌سرور و فریم‌ورک وب (مثل Django) هستن.
