from django.conf.urls import  include
from django.urls import path
from . import views

urlpatterns = [
  path('all/', views.MemberList.as_view()),
  path('create/', views.MemberCreate.as_view()),
  path('<int:pk>/', views.MemberDetail.as_view()),
  path('auth/', views.MemberDetail.as_view()), 
  

  path('save-expo-token/', views.SaveExpoTokenView.as_view()),
]
