from django.contrib.auth.decorators import login_required
from django.urls import path, include
from .views import loan_list
from . import views

urlpatterns = [
    path('', views.landing_page, name='landing'),
    path('register/', views.register, name='register'),
    path('loans/', views.loan_list, name='loan_list'),
    path('apply/', views.apply_for_loan, name='apply_for_loan'),
    path('accounts/', include('django.contrib.auth.urls')),
    # path('apply/', login_required(views.apply_for_loan), name='apply_loan'),
    path('pay/<int:loan_id>/', views.make_payment, name='make_payment'),
]
