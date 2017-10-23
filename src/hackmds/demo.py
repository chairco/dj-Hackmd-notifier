from django.conf import settings

import logging
import os
import sys
import django

logger = logging.getLogger(__name__)


BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# For test
if not settings.configured:
    """setting the Django env()"""
    logger.debug('settings.configured: {0}'.format(settings.configured))
    sys.path.append(BASE)
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.settings.local')
    django.setup()
    logger.debug('settings.configured: {0}'.format(settings.configured))
    from django.contrib.auth.models import User
    from hackmds.models import Archive

