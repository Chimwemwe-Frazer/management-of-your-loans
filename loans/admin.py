from django.contrib import admin
from .models import Borrower, Loan, Payment

admin.site.register(Borrower)
admin.site.register(Loan)
admin.site.register(Payment)
class BorrowerAdmin(admin.ModelAdmin):
    list_display = ("name", "phone")


