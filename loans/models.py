from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


# Create your models here.
class Borrower(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    address = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Loan(models.Model):
    borrower = models.ForeignKey(Borrower, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date_given = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    is_paid = models.BooleanField(default=False)

    
    def __str__(self):
        return f"Loan to {self.borrower.name}"

    def total_paid(self):
        return sum(payment.amount_paid for payment in self.payment_set.all())

    def remaining_balance(self):
        return self.amount - self.total_paid()
    
    def is_overdue(self):
        return not self.is_paid and timezone.now().date() > self.due_date
    
    def days_overdue(self):
        if self.is_overdue():
            return (timezone.now().date() - self.due_date).days
        return 0


class Payment(models.Model):
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    date_paid = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Payment for {self.loan}"


