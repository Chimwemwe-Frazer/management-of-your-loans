from django.core.exceptions import ValidationError
from PIL import Image, UnidentifiedImageError


MAX_DOCUMENT_SIZE = 5 * 1024 * 1024
ALLOWED_DOCUMENT_FORMATS = {"JPEG", "PNG", "WEBP"}


def validate_document_image(uploaded_file):
    if uploaded_file.size > MAX_DOCUMENT_SIZE:
        raise ValidationError("Each document must be no larger than 5 MB.")

    try:
        with Image.open(uploaded_file) as image:
            image_format = image.format
    except (Image.DecompressionBombError, OSError, UnidentifiedImageError, ValueError):
        raise ValidationError("Upload a valid JPEG, PNG, or WebP image.")
    finally:
        uploaded_file.seek(0)

    if image_format not in ALLOWED_DOCUMENT_FORMATS:
        raise ValidationError("Upload a valid JPEG, PNG, or WebP image.")
