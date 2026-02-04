from django.contrib import admin
from .models import Borrower, Loan, Payment

admin.site.register(Borrower)
admin.site.register(Loan)
admin.site.register(Payment)

# Register your models here.
