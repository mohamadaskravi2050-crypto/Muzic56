"""
ASGI config for muzic56 project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'muzic56.settings')

application = get_asgi_application()

#WSGI و ASGI هر دو interface (رابط) بین وب‌سرور و فریم‌ورک وب (مثل Django) هستن.
