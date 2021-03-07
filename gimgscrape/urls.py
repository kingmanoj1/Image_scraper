from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('downloaded/', views.search_and_download, name='search_and_download'),
]
