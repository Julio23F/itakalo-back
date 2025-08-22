from .views import verify_mailladdress_reset, verify_password_reset, confirm_password_reset, complete_password_reset, complete_email_reset, confirm_email_reset
from .change_password_view import change_password
from .reset_email_view import reset_email, complete_test
from django.urls import path
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('password/done/', complete_password_reset),
    path('password/confirm/', confirm_password_reset),
    path('password/<str:token>', change_password),
    path('email/done/', complete_email_reset),
    path('email/confirm/', confirm_email_reset),
    path('email/<str:token>', reset_email),
    path('email/test/', complete_test)
]