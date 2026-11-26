import tempfile
from pathlib import Path
from io import BytesIO
from decimal import Decimal
from datetime import date

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from PIL import Image

from .models import Borrower, Loan, Payment
from .validators import MAX_DOCUMENT_SIZE, validate_document_image


def image_upload(name):
    image_data = BytesIO()
    Image.new("RGB", (2, 2), color="blue").save(image_data, format="PNG")
    return SimpleUploadedFile(name, image_data.getvalue(), content_type="image/png")


class RepaymentProgressTests(TestCase):
    def setUp(self):
        user = User.objects.create_user(username="progress-borrower", password="test-pass")
        borrower = Borrower.objects.create(
            user=user,
            name="Progress Borrower",
            phone="555-0101",
        )
        self.loan = Loan.objects.create(
            borrower=borrower,
            amount=Decimal("100.00"),
            due_date=date(2026, 12, 31),
        )

    def test_repayment_progress_tracks_paid_amount(self):
        self.assertEqual(self.loan.repayment_progress(), 0)

        Payment.objects.create(loan=self.loan, amount_paid=Decimal("25.00"))
        self.assertEqual(self.loan.repayment_progress(), 25)

        Payment.objects.create(loan=self.loan, amount_paid=Decimal("75.00"))
        self.assertEqual(self.loan.repayment_progress(), 100)

    def test_days_until_due_tracks_upcoming_and_overdue_loans(self):
        today = timezone.now().date()
        self.loan.due_date = today + timedelta(days=5)
        self.loan.save(update_fields=["due_date"])
        self.assertEqual(self.loan.days_until_due(), 5)
        self.assertFalse(self.loan.is_overdue())

        self.loan.due_date = today - timedelta(days=3)
        self.loan.save(update_fields=["due_date"])
        self.assertTrue(self.loan.is_overdue())
        self.assertEqual(self.loan.days_overdue(), 3)


class BorrowerDocumentTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="borrower", password="test-pass")
        self.borrower = Borrower.objects.create(
            user=self.user,
            name="Test Borrower",
            phone="555-0100",
        )

    def private_storage_root(self):
        temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(temporary_directory.cleanup)
        return Path(temporary_directory.name)

    def test_first_loan_accepts_images_and_keeps_them_private(self):
        with override_settings(PRIVATE_MEDIA_ROOT=self.private_storage_root()):
            self.client.force_login(self.user)
            response = self.client.post(
                reverse("apply_for_loan"),
                {
                    "amount": "500",
                    "national_id_image": image_upload("national-id.png"),
                    "residence_map_image": image_upload("residence-map.png"),
                },
            )

            self.assertRedirects(response, reverse("loan_list"))
            self.assertEqual(Loan.objects.filter(borrower=self.borrower).count(), 1)

            self.borrower.refresh_from_db()
            self.assertTrue(self.borrower.national_id_image.storage.exists(
                self.borrower.national_id_image.name
            ))
            with self.assertRaises(ValueError):
                self.borrower.national_id_image.url

            download_url = reverse(
                "borrower_document",
                args=(self.borrower.pk, "national_id"),
            )
            response = self.client.get(download_url)
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response["Content-Disposition"].startswith("attachment;"))
            self.assertEqual(response["X-Content-Type-Options"], "nosniff")
            self.assertEqual(
                self.client.get("/media/national_ids/national-id.png").status_code,
                404,
            )

            other_user = User.objects.create_user(
                username="other",
                password="test-pass",
            )
            self.client.force_login(other_user)
            self.assertEqual(self.client.get(download_url).status_code, 404)

    def test_first_loan_rejects_fake_image_even_with_image_content_type(self):
        with override_settings(PRIVATE_MEDIA_ROOT=self.private_storage_root()):
            self.client.force_login(self.user)
            response = self.client.post(
                reverse("apply_for_loan"),
                {
                    "amount": "500",
                    "national_id_image": SimpleUploadedFile(
                        "fake.png",
                        b"not an image",
                        content_type="image/png",
                    ),
                    "residence_map_image": image_upload("residence-map.png"),
                },
            )

            self.assertRedirects(response, reverse("apply_for_loan"))
            self.assertFalse(Loan.objects.filter(borrower=self.borrower).exists())
            self.borrower.refresh_from_db()
            self.assertFalse(self.borrower.national_id_image)

    def test_oversized_document_is_rejected(self):
        oversized_file = SimpleUploadedFile(
            "large.png",
            b"x" * (MAX_DOCUMENT_SIZE + 1),
            content_type="image/png",
        )

        with self.assertRaises(ValidationError):
            validate_document_image(oversized_file)

    def test_document_upload_endpoint_uses_server_validation(self):
        with override_settings(PRIVATE_MEDIA_ROOT=self.private_storage_root()):
            self.client.force_login(self.user)
            response = self.client.post(
                reverse("upload_documents"),
                {
                    "national_id_image": SimpleUploadedFile(
                        "fake.png",
                        b"not an image",
                        content_type="image/png",
                    ),
                },
            )

            self.assertEqual(response.status_code, 200)
            self.borrower.refresh_from_db()
            self.assertFalse(self.borrower.national_id_image)
