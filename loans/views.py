from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta

from .models import Borrower, Loan, Payment


def landing_page(request):
    return render(request, "loans/landing.html")

def register(request):
    if request.method == "POST":
        user = User.objects.create_user(
            username=request.POST['username'],
            password=request.POST['password']
        )

        Borrower.objects.create(
            user=user,
            name=request.POST['name'],
            phone=request.POST['phone'],
            address=request.POST['address'],
        )

        login(request, user)
        return redirect('loan_list')

    return render(request, 'loans/register.html')


@login_required
def apply_for_loan(request):
    if request.user.is_superuser:
        messages.error(request, "Admins cannot apply for loans.")
        return redirect("loan_list")

    borrower = get_object_or_404(Borrower, user=request.user)

    borrower = Borrower.objects.get(user=request.user)

    has_previous_loan = Loan.objects.filter(borrower=borrower).exists()

    if request.method == "POST":
        if not has_previous_loan:
            national_id = request.FILES.get("national_id_image")
            residence_map = request.FILES.get("residence_map_image")

            if not national_id or not residence_map:
                messages.error(
                    request,
                    "National ID and Residence Map are required for your first loan."
                )
                return redirect("apply_for_loan")

            borrower.national_id_image = national_id
            borrower.residence_map_image = residence_map
            borrower.save()
        amount = request.POST.get("amount")
        due_date = timezone.now().date() + timedelta(days=30)

        Loan.objects.create(
            borrower=borrower,
            amount=amount,
            due_date=due_date,
            status='pending'
        )

        messages.success(request, "Loan application submitted successfully.")
        return redirect("loan_list")

    return render(
        request,
        "loans/apply_loan.html",
        {
            "has_previous_loan": has_previous_loan,
            "borrower": borrower
        }
    )

@login_required
def loan_list(request):
    loans = Loan.objects.filter(borrower__user=request.user)
    return render(request, "loans/loan_list.html", {"loans": loans})


@login_required
def make_payment(request, loan_id):
    loan = get_object_or_404(Loan, id=loan_id, borrower__user=request.user)

    if request.method == "POST":
        amount = float(request.POST.get("amount"))

        if amount <= 0:
            messages.error(request, "Payment amount must be positive.")
        elif amount > loan.remaining_balance():
            messages.error(request, "Payment cannot exceed remaining balance.")
        else:
            # Create the payment
            Payment.objects.create(
                loan=loan,
                amount_paid=amount
            )

            # Update is_paid if loan is fully repaid
            if loan.remaining_balance() == 0:
                loan.is_paid = True
                loan.save()

            messages.success(request, "Payment submitted successfully.")
            return redirect("loan_list")

    return render(request, "loans/make_payment.html", {"loan": loan})




@login_required
def payment_history(request, loan_id):
    loan = get_object_or_404(Loan, id=loan_id, borrower__user=request.user)
    payments = loan.payment_set.order_by('date_paid')  # ensure chronological order

    running_balance = loan.amount
    payment_list = []

    for payment in payments:
        running_balance -= payment.amount_paid
        payment_list.append({
            'date_paid': payment.date_paid,
            'amount_paid': payment.amount_paid,
            'remaining_balance': running_balance
        })

    return render(request, "loans/payment_history.html", {
        'loan': loan,
        'payments': payment_list,
        'total_paid': loan.total_paid(),
        'remaining_balance': loan.remaining_balance(),
    })

@login_required
def dashboard(request):
    borrower = request.user.borrower
    loans = borrower.loan_set.all()

    total_loans = loans.count()
    total_loaned_amount = sum(loan.amount for loan in loans)
    total_paid = sum(loan.total_paid() for loan in loans)
    total_remaining = sum(loan.remaining_balance() for loan in loans)
    overdue_loans = [loan for loan in loans if loan.is_overdue()]

    return render(request, 'loans/dashboard.html', {
        'loans': loans,
        'total_loans': total_loans,
        'total_loaned_amount': total_loaned_amount,
        'total_paid': total_paid,
        'total_remaining': total_remaining,
        'overdue_loans': overdue_loans,
    })
@login_required
def upload_documents(request):
    borrower = Borrower.objects.get(user=request.user)

    if request.method == "POST":
        borrower.national_id_image = request.FILES.get('national_id_image')
        borrower.residence_map_image = request.FILES.get('residence_map_image')
        borrower.save()

    return render(request, "upload_documents.html")


