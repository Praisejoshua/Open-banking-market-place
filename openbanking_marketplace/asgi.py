"""
ASGI config for Open Banking Marketplace Application.
"""
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'openbanking_marketplace.settings')

application = get_asgi_application()
