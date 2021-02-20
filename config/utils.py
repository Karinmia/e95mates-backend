import os
import uuid

from django.conf import settings


def show_toolbar(request):
    return settings.DEBUG


def get_file_path(instance, filename):
    """
    Rename images
    """
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join(instance.__class__.__name__.lower(), filename)
