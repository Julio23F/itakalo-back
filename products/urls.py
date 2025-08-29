from django.conf.urls import  include
from django.urls import path
from . import views

urlpatterns = [
    path('', views.ProductList.as_view()),
    path('create/', views.ProductCreate.as_view()),
    path('<int:pk>/', views.ProductDetail.as_view()),

    #Likes
    path('<int:product_id>/like/', views.ToggleLikeProductView.as_view(), name='toggle-like-product'),
]
