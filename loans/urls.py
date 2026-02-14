from django.contrib.auth.decorators import login_required
from django.urls import path, include
from .views import loan_list
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', views.landing_page, name='landing'),
    path('register/', views.register, name='register'),
    path('loans/', views.loan_list, name='loan_list'),
    path('apply/', views.apply_for_loan, name='apply_for_loan'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('pay/<int:loan_id>/', views.make_payment, name='make_payment'),
    path('loan/<int:loan_id>/payments/', views.payment_history, name='payment_history'),
    path('upload-documents/', views.upload_documents, name='upload_documents'),
    path('dashboard/', views.dashboard, name='dashboard')
] 
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
