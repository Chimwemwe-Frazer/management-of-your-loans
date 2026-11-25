from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_page, name='landing'),
    path('register/', views.register, name='register'),
    path('loans/', views.loan_list, name='loan_list'),
    path('apply/', views.apply_for_loan, name='apply_for_loan'),
    path('accounts/login/', views.CustomLoginView.as_view(), name='login'),
    path('pay/<int:loan_id>/', views.make_payment, name='make_payment'),
    path('loan/<int:loan_id>/payments/', views.payment_history, name='payment_history'),
    path('upload-documents/', views.upload_documents, name='upload_documents'),
    path(
        'borrowers/<int:borrower_id>/documents/<str:document_type>/',
        views.borrower_document,
        name='borrower_document',
    ),
    path('dashboard/', views.dashboard, name='dashboard'),
]