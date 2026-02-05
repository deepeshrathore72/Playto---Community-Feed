"""
Simple diagnostic view that doesn't require database.
"""
import os
from django.http import JsonResponse
from django.conf import settings


def diagnostic_view(request):
    """
    Simple diagnostic endpoint that works even if database is down.
    """
    return JsonResponse({
        'status': 'server_running',
        'debug': settings.DEBUG,
        'database_url_set': bool(os.environ.get('DATABASE_URL')),
        'allowed_hosts': settings.ALLOWED_HOSTS,
        'secret_key_set': bool(settings.SECRET_KEY and len(settings.SECRET_KEY) > 10),
        'python_version': os.environ.get('PYTHON_VERSION', 'not set'),
    })
