import filecmp

from django.conf import settings
from django.core.files import File
from django.core.files.storage import FileSystemStorage
from django.db import migrations, models

import loans.storage
import loans.validators


def transfer_documents(apps, source_storage, destination_storage):
    Borrower = apps.get_model("loans", "Borrower")
    document_names = set()
    for national_id, residence_map in Borrower.objects.values_list(
        "national_id_image",
        "residence_map_image",
    ):
        document_names.update(name for name in (national_id, residence_map) if name)

    for name in document_names:
        source_exists = source_storage.exists(name)
        destination_exists = destination_storage.exists(name)

        if not source_exists:
            if destination_exists:
                continue
            raise FileNotFoundError(f"Borrower document is missing from storage: {name}")

        if destination_exists:
            if not filecmp.cmp(
                source_storage.path(name),
                destination_storage.path(name),
                shallow=False,
            ):
                raise RuntimeError(f"Conflicting borrower document found: {name}")
            source_storage.delete(name)
            continue

        with source_storage.open(name, "rb") as source_file:
            saved_name = destination_storage.save(name, File(source_file))
        if saved_name != name:
            destination_storage.delete(saved_name)
            raise RuntimeError(f"Could not preserve borrower document name: {name}")
        source_storage.delete(name)


def move_documents_to_private_storage(apps, schema_editor):
    transfer_documents(
        apps,
        FileSystemStorage(location=settings.MEDIA_ROOT),
        loans.storage.PrivateDocumentStorage(),
    )


def restore_documents_to_media_storage(apps, schema_editor):
    transfer_documents(
        apps,
        loans.storage.PrivateDocumentStorage(),
        FileSystemStorage(location=settings.MEDIA_ROOT),
    )


class Migration(migrations.Migration):

    dependencies = [
        ("loans", "0004_loan_paid_date"),
    ]

    operations = [
        migrations.RunPython(
            move_documents_to_private_storage,
            restore_documents_to_media_storage,
        ),
        migrations.AlterField(
            model_name="borrower",
            name="national_id_image",
            field=models.ImageField(
                blank=True,
                null=True,
                storage=loans.storage.PrivateDocumentStorage(),
                upload_to="national_ids/",
                validators=[loans.validators.validate_document_image],
            ),
        ),
        migrations.AlterField(
            model_name="borrower",
            name="residence_map_image",
            field=models.ImageField(
                blank=True,
                null=True,
                storage=loans.storage.PrivateDocumentStorage(),
                upload_to="residence_maps/",
                validators=[loans.validators.validate_document_image],
            ),
        ),
    ]
