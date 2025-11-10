from django.urls import path
from . import views

urlpatterns = [
    path('', views.conseils, name='conseils'),
    path('backoffice/', views.backoffice_dashboard, name='backoffice_dashboard'),
    path('backoffice/establishments/', views.manage_establishments, name='manage_establishments'),
]