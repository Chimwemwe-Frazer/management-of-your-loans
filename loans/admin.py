from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import Borrower, Loan, Payment


@admin.register(Borrower)
class BorrowerAdmin(admin.ModelAdmin):
    list_display = ("name", "phone")
    readonly_fields = ("national_id_download", "residence_map_download")
    fields = (
        "user",
        "name",
        "phone",
        "address",
        "national_id_download",
        "residence_map_download",
    )

    @admin.display(description="National ID")
    def national_id_download(self, obj):
        if not obj or not obj.national_id_image:
            return "Not uploaded"
        url = reverse(
            "borrower_document",
            args=(obj.pk, "national_id"),
        )
        return format_html('<a href="{}">Download</a>', url)

    @admin.display(description="Residence map")
    def residence_map_download(self, obj):
        if not obj or not obj.residence_map_image:
            return "Not uploaded"
        url = reverse(
            "borrower_document",
            args=(obj.pk, "residence_map"),
        )
        return format_html('<a href="{}">Download</a>', url)


admin.site.register(Loan)
admin.site.register(Payment)


