from .views import verify_password_reset, confirm_password_reset, complete_password_reset
from .reset_password_view import reset_password
from django.urls import path
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('done/', complete_password_reset),
    path('confirm/', confirm_password_reset),
    path('email/<str:token>', reset_password),
]
