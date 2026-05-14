"""
WSGI config for Open Banking Marketplace Application.
"""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'openbanking_marketplace.settings')

application = get_wsgi_application()
