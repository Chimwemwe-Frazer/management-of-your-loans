from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.files.storage import FileSystemStorage
from django.utils.deconstruct import deconstructible
from pathlib import Path


@deconstructible
class PrivateDocumentStorage(FileSystemStorage):
    @property
    def location(self):
        private_root = Path(settings.PRIVATE_MEDIA_ROOT).resolve()
        media_root = Path(settings.MEDIA_ROOT).resolve()
        if private_root == media_root or media_root in private_root.parents:
            raise ImproperlyConfigured(
                "PRIVATE_MEDIA_ROOT must be outside MEDIA_ROOT."
            )
        return str(private_root)

    def url(self, name):
        raise ValueError("Private borrower documents do not have public URLs.")
