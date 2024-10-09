"""
ASGI config for backend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os

# import channls.asgi
from channels.routing import ProtocolTypeRouter
from django.core.asgi import get_asgi_application

django_asgi_app = get_asgi_application()

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
application = ProtocolTypeRouter({
    "http": django_asgi_app,
    # Just HTTP for now. (We can add other protocols later.)
})

ASGI_APPLICATION = 'backend.asgi.application'
