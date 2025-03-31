from django.urls import path
from agenda import views

urlpatterns = [
    path('', views.index, name = 'index'),
]