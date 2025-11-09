from django.urls import path
from . import views

urlpatterns = [
    #les routes vers les pages html
    path('', views.conseils, name='conseils'),
    path('backoffice/dashboard/', views.backoffice_dashboard, name='backoffice_dashboard'),
    path('backoffice/establishments/', views.manage_establishments, name='manage_establishments'),
    path('a-propos/', views.about, name='about'),
    path('actualites/', views.actualites, name='actualites'),
    path('s-inscrire/', views.register, name='register'),
    path('se-connecter/', views.user_login, name='login'),
]